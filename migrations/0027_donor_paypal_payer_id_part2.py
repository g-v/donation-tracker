# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools

from django.db import migrations, models
from django.db.models import Q
from django.core import validators
from django.core.exceptions import ValidationError

from tracker.viewutil import merge_donors
import tracker.util as util

def most_recent_donation_info(donorSet, Donation):
    foundDonations = Donation.objects.filter(donor__in=donorSet)
    trueEmail = None
    trueAlias = None
    mostRecentDonor = None
    if foundDonations.exists():
        for donation in foundDonations:
            mostRecentDonor = donation.donor
            if not trueEmail and donation.requestedemail:
                trueEmail = donation.requestedemail
            if not trueAlias and donation.requestedalias:
                trueAlias = donation.requestedalias
        for donation in foundDonations:
            if not trueEmail and donation.donor.email:
                trueEmail = donation.donor.email
            if not trueAlias and donation.donor.alias:
                trueAlias = donation.donor.alias
        for donation in foundDonations:
            if not trueEmail and donation.donor.paypalemail:
                trueEmail = donation.donor.paypalemail
    return trueEmail, trueAlias, mostRecentDonor
    
def assign_paypal_payer_id(apps, schema_editor):
    Donor = apps.get_model('tracker', 'Donor')
    Donation = apps.get_model('tracker', 'Donation')
    PayPalIPN = apps.get_model('ipn', 'PayPalIPN')

    for ipn in PayPalIPN.objects.filter(payment_status='Completed'):
        toks = ipn.custom.split(':')
        donationId = util.try_parse_int(toks[0]) if len(toks) > 0 else None
        if donationId != None:
            targetDonation = Donation.objects.filter(id=donationId)
            if targetDonation.exists() and targetDonation[0].donor != None:
                donor = targetDonation[0].donor
                #donor.paypalemail = ipn.payer_email
                donor.paypal_payer_id = ipn.payer_id
                #print("{0} : {1}".format(donor, donor.paypal_payer_id))
                donor.save()

def merge_donors_by_paypal_payer_id(apps, schema_editor):
    Donor = apps.get_model('tracker', 'Donor')
    Donation = apps.get_model('tracker', 'Donation')
    PayPalIPN = apps.get_model('ipn', 'PayPalIPN')

    payerIds = set()
    for donor in Donor.objects.filter(~Q(paypal_payer_id=None)):
        payerIds.add(donor.paypal_payer_id)
    for payerId in payerIds:
        donorSet = list(Donor.objects.filter(paypal_payer_id=payerId))
        if len(donorSet) > 1:
            trueEmail, trueAlias, mostRecentDonor = most_recent_donation_info(donorSet, Donation)
            if trueAlias not in list(map(lambda d: d.alias, donorSet)):
                trueAlias = None
            merge_donors(mostRecentDonor, donorSet)
            if trueAlias:
                mostRecentDonor.alias = trueAlias
            mostRecentDonor.email = trueEmail
            mostRecentDonor.save()
            print("Merged: {0} : {1}".format(mostRecentDonor, mostRecentDonor.paypal_payer_id))

def ensure_unique_email(apps, schema_editor):
    Donor = apps.get_model('tracker', 'Donor')
    PayPalIPN = apps.get_model('ipn', 'PayPalIPN')
    for donor in Donor.objects.all():
        matchingEmails = Donor.objects.filter(email=donor.email)
        if matchingEmails.count() > 1:
            for matchingDonor in matchingEmails:
                if not PayPalIPN.objects.filter(payer_id=matchingDonor.paypal_payer_id, payer_email=donor.email).exists():
                    if not matchingDonor.paypalemail:
                        foundMatches = PayPalIPN.objects.filter(payer_id=matchingDonor.paypal_payer_id)
                        if foundMatches.exists():
                            matchingDonor.email = foundMatches[0].payer_email
                        else:
                            matchingDonor.email = None
                    else:
                        matchingDonor.email = matchingDonor.paypalemail
                    print("Re-writing donor {0} : {1}".format(matchingDonor, matchingDonor.paypal_payer_id))
                    matchingDonor.save()
    
def ensure_actually_email(apps, schema_editor):
    Donor = apps.get_model('tracker', 'Donor')
    for donor in Donor.objects.all():
        try:
            validators.validate_email(donor.email)
        except ValidationError:
            donor.email = None
            donor.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0026_donor_paypal_payer_id_part1'),
        ('ipn', '__latest__')
    ]

    operations = [
        migrations.RunPython(assign_paypal_payer_id, lambda a,s: None),
        migrations.RunPython(merge_donors_by_paypal_payer_id, lambda a,s: None),
        migrations.RunPython(ensure_unique_email, lambda a,s: None),
        migrations.RunPython(ensure_actually_email, lambda a,s: None),
    ]
