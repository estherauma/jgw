from django.shortcuts import render
import json

# Create your views here.
def home(request):
    routes = [
            "bangladesh -> malaysia",
            "indonesia -> malaysia",
            "burma -> malaysia",
            "Greece -> uk",
            "nepal -> malaysia",
            "bangladesh -> mauritius",
            "Romania -> uk",
            "kenya -> qatar",
            "madagascar -> mauritius",
            "india -> malaysia",
            "kenya -> uae",
            "Bangladesh -> uk",
            "Bulgaria -> uk",
            "uganda -> saudi",
            "kenya -> saudi",
            "Ukraine -> uk",
            "vietnam -> malaysia",
            "Rest of the world -> uk",
            "India -> uk",
            "Italy -> uk",
            "pakistan -> malaysia"
        ]
    returning_data_list =  [68, 39, 36, 35, 27, 18, 19, 25, 10, 5, 4, 4, 3, 3, 3, 3, 2, 2, 1, 1, 1]
    unique_data_list = [100, 27, 55, 35, 27, 18, 12, 77, 10, 5, 4, 4, 3, 13, 3, 3, 2, 2, 13, 9, 1]

    return render(request, template_name="demo_dashboard/index.html", context={ 
            'routes':routes,
            'returning_data_list': returning_data_list,
            'unique_data_list': unique_data_list
    })


def demographics(request):
    return render(request, template_name="demo_dashboard/demographics.html")


def inline_question(request):
    data = {
        "origin": {
            "labels": ["Uzbekistan", "Kazakhstan", "Tajikistan", "Kyrgyzstan", "Other - The Rest Of The World", "Ukraine", "India", "Pakistan", "Nepal", "Britain (Uk)", "Russia", "South Africa", "Azerbaijan", "Georgia", "Albania", "Poland", "Bulgaria", "Indonesia", "Moldova", "Thailand", "Kenya", "Romania", "Estonia", "Serbia", "Vietnam", "Philippines", "Bangladesh"],
            "data": [117, 92, 84, 56, 43, 23, 19, 18, 16, 16, 15, 13, 6, 4, 4, 4, 3, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1]
        },
        "language": {
            "labels": ["Russian", "English", "Ukrainian", "Uzbek", "Bulgarian", "Nepali", "Albanian", "Indonesian", "Polish", "Romanian", "Serbian", "Vietnamese"],
            "data": [339, 163, 17, 12, 3, 3, 2, 2, 2, 1, 1, 1]
        },
        "question": {
            "labels": ["swsLabourProviderAskedToMakePayments", "recruiterKeptId", "areYouSure", "labourProviderAskedToMakePayment", "swsCopyOfContractInYourLanguage", "copyOfContractInYourLanguage", "swsAmountAskedToPay", "hadInductionTraining", "inductionLength", "paidForInductionTraining", "manageYourBankAccount", "correctHolidayPay", "paidCorrectNationalMinimumWage", "amountAskedToPay", "daysWithoutIds", "howMuchPerHour", "askForContractCopy", "askedToPayRecruitmentFee", "didYouHavePredepartureTraining", "contractInNativelanguage", "metInTimelyManner", "givenOrientation", "bankAccountExploitation", "swsLabourProviderAskedToMakePayment", "recruiterKeepID", "<br/><br/>copyOfContractInYourLanguage", "haveACallWithEmployerAboutTheJob", "researchedEmployer", "detailedJobOffer", "makePaymentToCompanyAccount", "agentAskedToMakePayment", "incorrectHolidayPay", "paidByEmployer", "wagesPaidToBankAccount", "paidAmountListedInContract", "providedWorkPlace", "readTrainingSection", "registeredRecruitmentAgency", "communicatedFullFinalAmountForJob", "nameAndAddressIncludedInContract", "foundGoodTestimoniesAboutAgency", "informedAboutRightsAndResponsibilities", "isAgentRegistered", "labourProviderFromRecognisedTradeAssociation", "askedToMakePayment", "payingIntoCompanyAccount", "communicatedAmountCharged", "employerNameAndAddressInContract", "givenOrientationAndInduction", "passportTakenAway", "passportUsedForResidentPermit", "passportReturned", "paidInYourBank", "providedSafeAndHygienicWorkPlace", "licensedLabourProvider", "labourProviderMemberOfTradeAssociation", "haveCopyOfContract", "trainingDuration", "paidNationalMinimumWage", "amountPerHour", "passportTaken", "passportUsedToGetResidentPermit", "employerOpenedPaidBankAccount", "openBankAccount"],
            "data": [378, 62, 53, 64, 67, 37, 7, 8, 4, 9, 22, 15, 31, 3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }

    }

    return render(request, template_name="demo_dashboard/inline_question.html",  context={ "data": json.dumps(data) })