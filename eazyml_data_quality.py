import os
import json
import sys
import getopt
sys.path.append("../client_code")
import eazyml as ez

AUTH_FILE = "authentication.json"
DATA_QUALITY_FILE = "data_quality.json"


def eazyml_auth(username, api_key, store_info=True):
    """
    Authenticate and store auth info in a file for future use

    Input:
        username: Email Id or username provided
        api_key: Api Key downloaded from UI
        store_info: Flag to store info for future use

    Return:
        Return authentication token used for sucessive calls to EazyML
    """
    resp = ez.ez_auth(username, api_key=api_key)
    if resp["success"] is True:
        print("Authentication successful")
        if store_info:
            content = {"username": username,
                       "api_key": api_key}
            json_obj = json.dumps(content, indent=4)
            with open(AUTH_FILE, "w") as fw:
                fw.write(json_obj)
            print("Authentication information is stored in %s" % (AUTH_FILE))
    else:
        print("Authentication error: %s" % (resp["message"]))
        return None
    return resp["token"]


def eazyml_data_quality(username, api_key, train_file_path=None, prefix="",
                        id_col="null", discard_col_list=[], shape="no",
                        balance="no", emptiness="no", impute="no",
                        outliers="no", remove_outlier="no", correlation="no",
                        data_drift="no", model_drift="no",
                        feature_importance="no", completeness="no",
                        correctness="no", outcome=None, test_file_path=None):
    """
    Run the EazyML operations based on the input

    """
    # Get Authentication token
    token = None
    if username and api_key:
        token = eazyml_auth(username, api_key, store_info=True)
    else:
        if os.path.exists(AUTH_FILE):
            auth_info = json.load(open(AUTH_FILE, "r"))
            token = eazyml_auth(auth_info["username"],
                                auth_info["api_key"])
        else:
            print("Please authenticate to proceed")
            return
    if train_file_path is None:
        return
    if impute == "yes" and emptiness == "no":
        emptiness = "yes"

    if emptiness == "yes":
        if impute == "no":
            accelerate = "yes"
        else:
            accelerate = "no"
    else:
        accelerate = "yes"

    if remove_outlier == "yes" and outliers == "no":
        outliers = "yes"

    options = {"data_shape": shape,
               "data_balance": balance,
               "data_emptiness": emptiness,
               "impute": impute,
               "data_outliers": outliers,
               "remove_outlier": remove_outlier,
               "outcome_correlation": correlation,
               "data_drift": data_drift,
               "model_drift": model_drift,
               "feature_importance": feature_importance,
               "data_completeness": completeness,
               "data_correctness": correctness,
               "data_quality_options":
                   {
                       "data_load_options": {
                                               "id": id_col,
                                               "impute": "no",
                                               "outlier": "no",
                                               "discard": discard_col_list,
                                               "accelerate": accelerate,
                                            }
                   },
               "prediction_filename": test_file_path,
               }

    # GETTING THE dataset_id FROM THE OUTPUT DICTIONARY of ez_load
    resp = ez.ez_data_quality(token, train_file_path, outcome, options)
    # dumping the results in json files
    quality_obj = json.dumps(resp, indent=4)
    dump_file = prefix + "_" + DATA_QUALITY_FILE

    with open(dump_file, "w") as fw:
        fw.write(quality_obj)
    print("The response for data quality assessment",
          "is stored in %s" % (dump_file))


if __name__ == "__main__":
    args_list = sys.argv[1:]
    # Options
    options = "h:u:p:x:" + \
              "f:o:i:c:" + \
              "sbe" + \
              "ul" + \
              "rnd" + \
              "mt" + \
              "agz:"
    long_options = ["help", "username=", "api_key=", "prefix_name=",
                    "train_file=", "outcome=", "id_col=", "discard_col_list=",
                    "data_shape", "data_balance", "data_emptiness",
                    "impute", "data_outliers",
                    "remove_outliers", "data_correlation", "data_drift",
                    "model_drift", "feature_importance",
                    "data_completeness", "data_correctness", "test_file="]
    username = api_key = config_file = None
    train_file_path = outcome = id_col = test_file_path = None
    discard_col_list = []
    shape = balance = "no"
    emptiness = impute = "no"
    outliers = remove_outlier = "no"
    correlation = "no"
    data_drift = model_drift = "no"
    feature_importance = completeness = correctness = "no"
    prefix_name = "EazyML"
    try:
        # Parsing argument
        arguments, values = getopt.getopt(args_list, options, long_options)
        # checking each argument
        for curr_arg, curr_val in arguments:
            print(curr_arg, curr_val)
            if curr_arg in ("-h", "--help"):
                print("".join(open("help.txt", "r").readlines()))
                exit()
            elif curr_arg in ("-u", "--username"):
                username = curr_val
            elif curr_arg in ("-p", "--api_key"):
                api_key = curr_val
            elif curr_arg in ("-x", "--prefix_name"):
                prefix_name = curr_val
            elif curr_arg in ("-f", "--train_file"):
                train_file_path = curr_val
            elif curr_arg in ("-o", "--outcome"):
                outcome = curr_val
            elif curr_arg in ("-i", "--id_col"):
                id_col = curr_val
            elif curr_arg in ("-c", "--discard_col_list"):
                discard_col_list = [x.strip() for x in curr_val.split(",")]
            elif curr_arg in ("-s", "--data_shape"):
                shape = "yes"
            elif curr_arg in ("-b", "--data_balance"):
                balance = "yes"
            elif curr_arg in ("-e", "--data_emptiness"):
                emptiness = "yes"
            elif curr_arg in ("-u", "--impute"):
                impute = "yes"
            elif curr_arg in ("-l", "--data_outliers"):
                outliers = "yes"
            elif curr_arg in ("-r", "--remove_outliers"):
                remove_outlier = "yes"
            elif curr_arg in ("-n", "--data_correlation"):
                correlation = "yes"
            elif curr_arg in ("-d", "--data_drift"):
                data_drift = "yes"
            elif curr_arg in ("-m", "--model_drift"):
                model_drift = "yes"
            elif curr_arg in ("-t", "--feature_importance"):
                feature_importance = "yes"
            elif curr_arg in ("-a", "--data_completeness"):
                completeness = "yes"
            elif curr_arg in ("-g", "--data_correctness"):
                correctness = "yes"
            elif curr_arg in ("-z", "--test_file"):
                test_file_path = curr_val
        eazyml_data_quality(username, api_key, train_file_path, prefix_name,
                            id_col, discard_col_list, shape, balance,
                            emptiness, impute, outliers, remove_outlier,
                            correlation, data_drift, model_drift,
                            feature_importance, completeness, correctness,
                            outcome, test_file_path)

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))
