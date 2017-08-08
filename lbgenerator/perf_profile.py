# -*- coding: utf-8 -*-
"""Auxiliar em investigar problemas de performance."""

import time
import datetime


class ProfileItem():
    def __init__(self, prof_item_alias, prof_item_desc=None, prof_item_group=None):
        self.prof_item_alias = prof_item_alias

        if not prof_item_desc:
            self.prof_item_desc = self.prof_item_alias
        else:
            self.prof_item_desc = prof_item_desc

        self.prof_item_group = prof_item_group
        self.start_sw_val = None
        self.elapsed_time = None

    def start_sw(self, time_now):
        self.start_sw_val = time_now

    def stop_sw(self, time_now):
        elapsed_time_now = time_now - self.start_sw_val
        self.start_sw_val = -1
        if not self.elapsed_time:
            self.elapsed_time = elapsed_time_now
        else:
            self.elapsed_time = self.elapsed_time + elapsed_time_now

class PerfProfile():
    def __init__(self, no_log=False, overw_log=True, log_path="", allowed_groups=[], reverse_allow=False):

        self.no_log = no_log
        self.log_fn = None
        self.overw_log = overw_log
        self.allowed_groups = allowed_groups
        self.reverse_allow = reverse_allow

        if log_path:
            self.log_path = log_path + "/"
        else:
            self.log_path = ""

        self.profile_items={}
        self.glob_start_time = None
        self.glob_stop_time = -1
        self.glob_elapsed_time = -1
        pass

    def reset(self):
        self.profile_items={}
        self.glob_start_time = None
        pass

    def allow_group(self, prof_item_groups=[]):
        for prof_item_group in prof_item_groups:
            if not prof_item_group in self.allowed_groups:
                self.allowed_groups.append(prof_item_group)

    def start_sw(self, prof_item_alias):
        time_now = time.time()

        if not prof_item_alias in self.profile_items:
            return

        self.profile_items[prof_item_alias].start_sw(time_now)

    def stop_sw(self, prof_item_alias):
        time_now = time.time()

        if not prof_item_alias in self.profile_items:
            return

        self.profile_items[prof_item_alias].stop_sw(time_now)

    def add_prof_item(self, prof_item_alias, prof_item_desc=None, prof_item_group=None):
        time_now = time.time()

        if not self.reverse_allow:
            if self.allowed_groups:
                if not prof_item_group in self.allowed_groups:
                    return
        else:
            if prof_item_group in self.allowed_groups:
                return

        if not self.glob_start_time:
            self.glob_start_time = time_now

        if prof_item_alias in self.profile_items:
            return

        profile_item=ProfileItem(prof_item_alias, prof_item_desc, prof_item_group)
        self.profile_items[profile_item.prof_item_alias] = profile_item

    def format_num(self, number_val, prec=9):
        return ("%." + str(prec) + "f") % number_val

    def get_percent(self, item_elapsed_time):
        return ((item_elapsed_time * 100) / self.glob_elapsed_time)

    def get_report(self):
        self.glob_stop_time = time.time()

        if not self.log_fn:
            if self.overw_log:
                self.log_fn = "pp_f_log.log"
            else:
                self.log_fn = datetime.datetime.now().strftime(
                    'pp_%Y-%m-%d-%H-%M-%S.log')

        adjust_factor=0.0
        # adjust_factor=0.010299921
        self.glob_elapsed_time = self.glob_stop_time - (self.glob_start_time + adjust_factor)

        prof_items_lt = []
        prof_items_group = {}
        for key in self.profile_items:
            profile_item = self.profile_items[key]
            prof_items_lt.append([
                profile_item.prof_item_alias, 
                profile_item.elapsed_time
            ])

            if not profile_item.prof_item_group in prof_items_group:
                prof_items_group[profile_item.prof_item_group] = \
                    profile_item.elapsed_time
            else:
                prof_items_group[profile_item.prof_item_group] += \
                    profile_item.elapsed_time

        prof_items_gp_lt = []
        for key in prof_items_group:
            prof_item_group = prof_items_group[key]
            prof_items_gp_lt.append([
                key, 
                prof_items_group[key]
            ])
        prof_items_group = None

        def getIndex(item):
            return item[1]
        prof_items_gp_lt_st = sorted(prof_items_gp_lt, key=getIndex, reverse=True)
        prof_items_lt_st = sorted(prof_items_lt, key=getIndex, reverse=True)

        op = ""
        op = op + ">>>> ------------------------------------------------\n"
        op = op + "PROFILE REPORT\n"
        op = op + "(in " + str(datetime.datetime.now()) + ")\n(time in secs)\n"
        op = op + "-------------------\n"
        for prof_item_lt_st in prof_items_lt_st:
            profile_item = self.profile_items[prof_item_lt_st[0]]
            profile_item.elapsed_time = profile_item.elapsed_time - adjust_factor
            op = op + "> ----------------------------\n"

            prof_item_group = ""
            if profile_item.prof_item_group:
                prof_item_group = " (GROUP: " \
                    + profile_item.prof_item_group + ")"

            op = op + "NAME ...... : " + profile_item.prof_item_alias + \
                prof_item_group + "\n"
            op = op + "DESCRIPTION : " + profile_item.prof_item_desc + "\n"
            op = op + "ELAPSED TIME: " + str(\
                self.format_num(profile_item.elapsed_time)) + "\n"
            op = op + "PERCENT ... : " + str(self.format_num(
                self.get_percent(profile_item.elapsed_time), 2)) + "%\n"
            op = op + "< ----------------------------\n"

        if len(prof_items_gp_lt_st) > 0:
            op = op + "\n"
            op = op + "> -------------------------------------\n"
            op = op + "GROUPS\n"

        for prof_item_gp_lt_st in prof_items_gp_lt_st:
            op = op + "> ----------------------------\n"
            op = op + "NAME ...... : " + str(prof_item_gp_lt_st[0]) + "\n"
            op = op + "ELAPSED TIME: " + str(prof_item_gp_lt_st[1]) + "\n"
            op = op + "PERCENT ... : " + str(self.format_num(
                self.get_percent(prof_item_gp_lt_st[1]), 2)) + "%\n"
            op = op + "< ----------------------------\n"

        if len(prof_items_gp_lt_st) > 0:
            op = op + "< -------------------------------------\n"

        op = op + "\n"
        op = op + "TOTAL ELAPSED TIME: " + str(\
            self.format_num(self.glob_elapsed_time)) + "\n"
        op = op + "< ---------------------------------------------------\n"

        if not self.no_log:

            with open(self.log_path + self.log_fn, "a") as text_file:
                text_file.write(op)

        return op

pprofile=PerfProfile(no_log=False, overw_log=True, log_path="/usr/local/lb/lbg_ve32/src/LBGenerator", allowed_groups=[], reverse_allow=False)
