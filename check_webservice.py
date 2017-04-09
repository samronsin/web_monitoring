#!/usr/bin/python

import sys
import argparse
import os.path as osp
import json
import requests
import smtplib

#################
# health checks #
#################


def get_state_file(service, check):
    return osp.join(osp.dirname(__file__), "services", service, check)


def get_old_state(state_file):
    return osp.isfile(state_file)


def get_new_state(urls, verbose=False):
    global VERBOSE
    state_ok = True
    for url in urls:
        if VERBOSE:
            print("checking url: {}".format(url))
        state_ok = state_ok and check_url(url)
        if not state_ok:
            return False
    return True


def check_url(url):
    res = requests.get(url)
    return res.status_code == 200


def update_state(state_file, is_ok):
    assert type(is_ok) == bool
    if is_ok:
        open(state_file, 'a').close() # touch
    else:
        os.remove(state_file)


########
# misc #
########

parser = argparse.ArgumentParser(description="Check web services and alert whenever down or back up.")
parser.add_argument("--service", required=True)
parser.add_argument("--check", required=True)
parser.add_argument("--verbose", "-v", required=False, action="store_true")


def notify(j_config, check, is_ok):
    message = j_config["checks"][check]["state_ok_message" if is_ok else "state_problem_message"]
    sender = j_config["alert"]["sender"]
    receivers = j_config["alert"]["receivers"]
    smtp_conn = smtplib.SMTP("smtp.gmail.com", 587)
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
    check = j_config["checks"].get(CHECK)
    if check is None:
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
