import traceback
import json

from django.dispatch import receiver
from django.core import serializers

from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received

import post_office

import tracker.models as models
import tracker.viewutil as viewutil
import tracker.paypalutil as paypalutil


@receiver(valid_ipn_received, dispatch_uid='tracker.signals.valid_ipn_received_signal')
def valid_ipn_received_signal(sender, **kwargs):
    ipnObj = sender
    try:
        donation = paypalutil.initialize_paypal_donation(ipnObj)
        donation.save()

        if donation.transactionstate == 'PENDING':
            reasonExplanation, ourFault = paypalutil.get_pending_reason_details(ipnObj.pending_reason)
            if donation.event.pendingdonationemailtemplate:
                formatContext = {
                    'event': donation.event,
                    'donation': donation,
                    'donor': donor,
                    'pending_reason': ipnObj.pending_reason,
                    'reason_info': reasonExplanation if not ourFault else '',
                }
                post_office.mail.send(recipients=[donation.donor.email], sender=donation.event.donationemailsender, template=donation.event.pendingdonationemailtemplate, context=formatContext)
            # some pending reasons can be a problem with the receiver account, we should keep track of them
            if ourFault:
                paypalutil.log_ipn(ipnObj, 'Unhandled pending error')
        elif donation.transactionstate == 'COMPLETED':
            if donation.event.donationemailtemplate != None:
                formatContext = {
                    'donation': donation,
                    'donor': donation.donor,
                    'event': donation.event,
                    'prizes': viewutil.get_donation_prize_info(donation),
                }
                post_office.mail.send(recipients=[donation.donor.email], sender=donation.event.donationemailsender, template=donation.event.donationemailtemplate, context=formatContext)

            # TODO: this should eventually share code with the 'search' method's way
            # of dumping data to json
            postbackData = {
                'id': donation.id,
                'timereceived': str(donation.timereceived),
                'comment': donation.comment,
                'amount': donation.amount,
                'donor__visibility': donation.donor.visibility,
                'donor__visiblename': donation.donor.visible_name(),
            }
            
            postbacks = models.PostbackURL.objects.filter(event=donation.event)
            if postbacks.exists():
                postbackJSon = json.dumps(postbackData, ensure_ascii=False, cls=serializers.json.DjangoJSONEncoder)
                for postback in postbacks:
                    opener = urllib2.build_opener()
                    req = urllib2.Request(postback.url, postbackJSon, headers={'Content-Type': 'application/json; charset=utf-8'})
                    response = opener.open(req, timeout=5)
        elif donation.transactionstate == 'CANCELLED':
            # eventually we may want to send out e-mail for some of the possible cases
            # such as payment reversal due to double-transactions (this has happened before)
            paypalutil.log_ipn(ipnObj, 'Cancelled/reversed payment')

    except Exception as inst:
        # just to make sure we have a record of it somewhere
        print("ERROR IN IPN RESPONSE, FIX IT")
        if ipnObj:
            paypalutil.log_ipn(ipnObj, "{0} \n {1}.".format(inst, traceback.format_exc(inst)))
        else:
            viewutil.tracker_log('paypal', 'IPN creation failed: {0} \n {1}.'.format(inst, traceback.format_exc(inst)))


@receiver(invalid_ipn_received, dispatch_uid='tracker.signals.invalid_ipn_received_signal')
def invalid_ipn_received_signal(sender, **kwargs):
    ipnObj = sender
    paypalutil.log_ipn(ipnObj, "Flagged IPN Object")

