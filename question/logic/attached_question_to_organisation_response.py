from preference.models import Organisation
from question.models import InlineQuestionResponse


myvoice = [
    "agentAskedToMakePayment",
    "makePaymentToCompanyAccount",
    "detailedJobOffer",
    "nameAndAddressIncludedInContract",
    "researchedEmployer",
    "metInTimelyManner",
    "givenOrientation",
    "paidByEmployer",
    "wagesPaidToBankAccount",
    "paidAmountListedInContract",
    "providedWorkPlace",
    "passportTaken",
    "passportUsedToGetResidentPermit",
    "passportReturned",
    "recentJobSearchPayment"
]

evergreen = [
    "evergreenDidYouAttendInterview",
    "evergreenDoYouKnowEvergreenEmployer",
    "evergreenDidYouPayAnyone",
    "evergreenBriefedContractInNepali",
    "evergreenContractInNepali",
    "evergreenAvailableComplaintChannels",
    "evergreenHiredZeroCost"
]

def update_organisation_inline_question():
   

    myvoice_set = set(myvoice)
    evergreen_set = set(evergreen)

    not_specified_organisation = Organisation.objects.get(name="not specified")
    responses = InlineQuestionResponse.objects.select_related('inline_question__question')

    for response in responses:
        question_text = response.inline_question.question.text
        if question_text in myvoice_set:
            response.organisation_inline_question = "myvoice"
            response.save()
            response.inline_question.inline_question_standard.organisation = not_specified_organisation
            response.inline_question.inline_question_standard.save()
        elif question_text in evergreen_set:
            response.organisation_inline_question = "evergreen"
            response.save()
        else:
            continue