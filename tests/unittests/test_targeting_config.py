import unittest
import os

from emod_api import campaign as api_campaign
import emodpy_hiv.utils.targeting_config as tc

from pathlib import Path
import sys
manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest


class TestTargetingConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(manifest.eradication_path):
            print(f'Eradication does not exist, writing it to {manifest.package_folder}.')
            import emod_hiv.bootstrap as dtk
            dtk.setup(manifest.package_folder)
        cls.campaign = api_campaign  # Initialize the campaign object
        cls.campaign.set_schema(manifest.schema_path)  # set the schema path to the HIV schema file

    def setUp(self):
        print(f"running test: {self.__class__}.{self._testMethodName}")


    def test_IsCircumcised(self):
        """
        Test the IsCircumcised targeting config filter and see that it creates the proper JSON.
        """
        tc_obj = tc.IsCircumcised()

        exp_json = {
            "class": "IsCircumcised",
            "Is_Equal_To": 1
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )


    def test_IsHivPositive(self):
        """
        Test the IsHivPositive targeting config filter and see that it creates the proper JSON.
        """
        tc_obj = tc.IsHivPositive( and_has_ever_been_tested=tc.YesNoNa.YES,
                                   and_has_ever_tested_positive=tc.YesNoNa.YES,
                                   and_has_received_positive_results=tc.YesNoNa.NO)

        exp_json = {
            "class": "IsHivPositive",
            "Is_Equal_To": 1,
            "And_Has_Ever_Been_Tested" : "YES",
            "And_Has_Ever_Tested_Positive" : "YES",
            "And_Has_Received_Positive_Results" : "NO"
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )


    def test_IsOnART(self):
        """
        Test the IsOnART targeting config filter and see that it creates the proper JSON.
        """
        tc_obj = tc.IsOnART()

        exp_json = {
            "class": "IsOnART",
            "Is_Equal_To": 1
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )


    def test_IsPostDebut(self):
        """
        Test the IsPostDebut targeting config filter and see that it creates the proper JSON.
        """
        tc_obj = tc.IsPostDebut()

        exp_json = {
            "class": "IsPostDebut",
            "Is_Equal_To": 1
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )


    def test_HasBeenOnArtMoreOrLessThanNumMonths(self):
        """
        Test the HasBeenOnArtMoreOrLessThanNumMonths targeting config filter and see that it creates the proper JSON.
        """
        tc_obj = tc.HasBeenOnArtMoreOrLessThanNumMonths( num_months=7, more_or_less=tc.MoreOrLess.MORE )

        exp_json = {
            "class": "HasBeenOnArtMoreOrLessThanNumMonths",
            "Is_Equal_To": 1,
            "Num_Months" : 7,
            "More_Or_Less" : "MORE"
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )


    def test_HasMoreOrLessThanNumPartners(self):
        """
        Test the HasMoreOrLessThanNumPartners targeting config filter and see that it creates the proper JSON.
        """
        tc_obj = tc.HasMoreOrLessThanNumPartners( num_partners=2,
                                                  more_or_less=tc.MoreOrLess.MORE,
                                                  of_relationship_type=tc.OfRelationshipType.COMMERCIAL)

        exp_json = {
            "class": "HasMoreOrLessThanNumPartners",
            "Is_Equal_To": 1,
            "Num_Partners" : 2,
            "More_Or_Less" : "MORE",
            "Of_Relationship_Type" : "COMMERCIAL"
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )


    def test_HasHadMultiplePartnersInLastNumMonths(self):
        """
        Test the HasHadMultiplePartnersInLastNumMonths targeting config filter and see that it creates the proper JSON.
        """
        tc_obj = tc.HasHadMultiplePartnersInLastNumMonths( num_month_type=tc.NumMonthsType.SIX_MONTHS,
                                                           of_relationship_type=tc.OfRelationshipType.INFORMAL)

        exp_json = {
            "class": "HasHadMultiplePartnersInLastNumMonths",
            "Is_Equal_To": 1,
            "Num_Months_Type" : "SIX_MONTHS",
            "Of_Relationship_Type" : "INFORMAL"
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )


    def test_HasCd4BetweenMinAndMax(self):
        """
        Test the HasCd4BetweenMinAndMax targeting config filter and see that it creates the proper JSON.
        """
        tc_obj = tc.HasCd4BetweenMinAndMax( min_cd4=500.0, max_cd4=1000.0 )

        exp_json = {
            "class": "HasCd4BetweenMinAndMax",
            "Is_Equal_To": 1,
            "Min_CD4" : 500.0,
            "Max_CD4" : 1000.0
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )


    def test_HasRelationship(self):
        """
        Test the HasRelationship targeting config filter and see that it creates the proper JSON.
        """

        tc_obj = tc.HasRelationship( of_relationship_type=tc.OfRelationshipType.TRANSITORY,
                                    that_recently=tc.RecentlyType.ENDED,
                                    that_recently_ended_due_to=tc.RelationshipTerminationReasonType.PARTNER_DIED,
                                    with_partner_who=(tc.IsHivPositive() & tc.IsOnART()) )

        exp_json = {
            "class": "HasRelationship",
            "Is_Equal_To": 1,
            "Of_Relationship_Type" : "TRANSITORY",
            "That_Recently": "ENDED",
            "That_Recently_Ended_Due_To": "PARTNER_DIED",
            "With_Partner_Who" : {
                "class" : "TargetingLogic",
                "Is_Equal_To": 1,
                "Logic": [
                    [
                        {
                            "class": "IsHivPositive",
                            "Is_Equal_To": 1,
                            "And_Has_Ever_Been_Tested" : "NA",
                            "And_Has_Ever_Tested_Positive" : "NA",
                            "And_Has_Received_Positive_Results" : "NA"
                        },
                        {
                            "class": "IsOnART",
                            "Is_Equal_To": 1,
                        }
                    ]
                ]
            }
        }

        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )

        tc_obj = tc.HasRelationship( of_relationship_type=tc.OfRelationshipType.TRANSITORY,
                                     that_recently=tc.RecentlyType.ENDED,
                                     that_recently_ended_due_to=tc.RelationshipTerminationReasonType.PARTNER_DIED,
                                     with_partner_who=None )

        exp_json = {
            "class": "HasRelationship",
            "Is_Equal_To": 1,
            "Of_Relationship_Type" : "TRANSITORY",
            "That_Recently": "ENDED",
            "That_Recently_Ended_Due_To": "PARTNER_DIED"
        }
        self.assertDictEqual( exp_json, tc_obj.to_simple_dict(self.campaign) )



if __name__ == "__main__":
    import unittest
    unittest.main()
