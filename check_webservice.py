#!/usr/bin/python

""" Check health of a configured web service """


import os
import argparse
import os.path as osp
import json
import smtplib
import requests

#################
# health checks #
#################


def get_state_file(service, check):
    """ Return the relevant path for service and check """
    return osp.join(osp.dirname(__file__), "services", service, check)


def get_old_state(state_file):
    """ Fetch last state as recorded on the local filesystem """
    return osp.isfile(state_file)


def get_new_state(urls, verbose=False):
    """ Check all the urls and return True iff all urls are healthy """
    global VERBOSE
    state_ok = True
    for url in urls:
        if VERBOSE:
            print "checking url: {}".format(url)
        state_ok = state_ok and check_url(url)
        if not state_ok:
            return False
    return True


def check_url(url):
    """ Check if url responds to get request with 200 status code """
    try:
        res = requests.get(url)
        return res.status_code == 200
    except:
        return False

def update_state(state_file, is_ok):
    """ Update the state as a record on the local filesystem """
    assert isinstance(is_ok, bool)
    if is_ok:
        open(state_file, 'a').close()  # touch
    else:
        os.remove(state_file)


########
# misc #
########

desc = "Check web services and alert whenever down or back up."
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("--service", required=True)
parser.add_argument("--check", required=True)
parser.add_argument("--verbose", "-v", required=False, action="store_true")


def notify(j_config, check, is_ok):
    """ Send notification to registered email address """
    message = j_config["checks"][check]["state_ok_message" if is_ok else "state_problem_message"]
    sender = j_config["alert"]["sender"]
    receivers = j_config["alert"]["receivers"]
    PORT = sender.get("port")
    if  is None:
        PORT = 587
    smtp_conn = smtplib.SMTP(sender["server"], PORT)
    smtp_conn.starttls()
    smtp_conn.login(sender["login"], sender["password"])
    smtp_conn.sendmail(sender["address"], receivers, message)
    smtp_conn.quit()


########
# main #
########


if __name__ == "__main__":
    args = parser.parse_args()
    SERVICE = args.service
    CHECK = args.check
    VERBOSE = args.verbose
    config_path = osp.join(osp.dirname(__file__), "services", SERVICE, "config.json")
    with open(config_path) as config_file:
        j_config = json.loads(config_file.read())
    if j_config["checks"].get(CHECK) is None:
        raise Exception("No check named {} for service {}".format(CHECK, SERVICE))
    state_file = get_state_file(SERVICE, CHECK)
    was_ok = get_old_state(state_file)
    if VERBOSE:
        print "was ok: {}".format(was_ok)
    urls = j_config["checks"][CHECK]["urls"]
    is_ok = get_new_state(urls)
    if VERBOSE:
        print "is ok: {}".format(is_ok)
    if was_ok != is_ok:
        if VERBOSE:
            print "updating state and sending alerts..."
        update_state(state_file, is_ok)
        notify(j_config, CHECK, is_ok)
    if VERBOSE:
        print "done"
