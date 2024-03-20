import requests
import lxml.html
import re
import sys
import time
import datetime


class Legislator:
    def __init__(
            self, state, data_source, name=None, chamber=None, district=None,
            party=None, image=None, email=None, webpage=None, title=None,
            address=None, phone=None, fax=None
    ):
        self.state = state
        self.data_source = data_source
        self.name = name
        self.chamber = chamber
        self.district = district
        self.party = party
        self.image = image
        self.email = email
        self.webpage = webpage
        self.title = title
        self.address = address
        self.phone = phone
        self.fax = fax
        self.social_handles = {}

    def __repr__(self):
        return (f"Legislator(name={self.name}, state={self.state}, "
                f"chamber={self.chamber}, district={self.district}, "
                f"party={self.party}, image={self.image}, email={self.email}, "
                f"webpage={self.webpage}, title={self.title}, "
                f"address={self.address}, phone={self.phone}, "
                f"fax={self.fax}, social_handles={self.social_handles})")


class HawaiiLegislature:
    def __init__(self):
        self.source = (
            "https://www.capitol.hawaii.gov/members/legislators.aspx"
        )
        self.selector = ".//div[@class='contact-box center-version active']"
        self.members = {"House": {}, "Senate": {}}

        self.email_removal = [" iii", "jr.", " ", "-"]
        self.email_remove_regexes = [
            re.compile(string) for string in self.email_removal]
        self.leader_regex = re.compile(r"(.+),(.+)\s+\(([A-Z]+)\)\s+(.+)")
        self.multi_commas_regex = re.compile(r",.+,")
        self.regular_regex = re.compile(r"(.+),(.+)\s+\(([A-Z]+)\)")
        self.social_plat_and_hand_re = re.compile(
            r"\.*/*(\w+)\.com/(.+)")
        self.social_removal = [
            "user", "channel", "playlists", "photos", "/", "@"
        ]
        self.social_remove_regexes = [
            re.compile(string) for string in self.social_removal]

    def process_list(self, update_progress):
        response = requests.get(self.source)
        if response.status_code == 200:
            content = lxml.html.fromstring(response.content)
            items = content.xpath(self.selector)
            total_items = len(items)
            if not items:
                print(f"Failed to retrieve list from {self.source}")
                return
            for index, item in enumerate(items):
                self.process_member(item)
                update_progress(index + 1, total_items)
        else:
            print(f"Failed to retrieve {self.source}")
            return

    def process_member(self, item):
        leg = Legislator(state="hi", data_source=self.source)

        a_tag = item.xpath("a")[0]
        url_base = "https://www.capitol.hawaii.gov/"
        leg.webpage = url_base + str(a_tag.get('href'))
        leg.image = url_base + str(a_tag.xpath('img')[0].get('src'))

        member_text = a_tag.text_content().strip()

        multi_commas = self.multi_commas_regex.search(member_text)
        if multi_commas:
            single_line = member_text.replace("\r\n", "")
            comma_split = [x.strip() for x in single_line.split(",")]
            member_text = f"{' '.join(comma_split[0:2])}, {comma_split[-1]}"

        leader = self.leader_regex.search(member_text)
        if leader:
            name_parts = [x.strip() for x in leader.groups()]
            leg.title = name_parts.pop()
        else:
            regular_member = self.regular_regex.search(member_text)
            name_parts = [x.strip() for x in regular_member.groups()]

        leg.party = "Democratic" if name_parts.pop() == "D" else "Republican"

        last_name, first_name = name_parts[0], " ".join(name_parts[1:])
        leg.name = f"{first_name} {last_name}"

        dist_text = item.xpath("div/a")[0].text_content().strip()
        chamber, leg.district = [
            x.strip() for x in dist_text.split("District")
        ]
        leg.chamber = "House" if chamber[0] == "H" else "Senate"

        # TODO: explore replacing below workaround method with solution for
        #  Cloudflare email encryption, see on SO: https://tinyurl.com/ytbajeum
        #   For now, below workaround has been manually checked for accuracy,
        #   but will likely fail in future when legislators share a last name.
        userbase = last_name.lower()
        for string in self.social_remove_regexes:
            userbase = string.sub("", userbase)
        email_pref = {"House": "rep", "Senate": "sen"}
        leg.email = email_pref[leg.chamber] + userbase + "@capitol.hawaii.gov"

        contact_data = item.xpath("div/address")
        if contact_data:
            self.process_contact_info(contact_data[0], leg)

        self.members[leg.chamber][leg.district] = leg
        return

    def process_contact_info(self, contact_info, legis):
        split_lines = contact_info.text_content().split("\r\n")
        contact_list = [x.strip() for x in split_lines if len(x.strip())]

        state_addr_base = "415 S Beretania St, Honolulu, HI 96813"
        legis.address = f"{contact_list[0]}, {state_addr_base}"
        legis.phone, legis.fax = [
            x.split(":")[-1].strip() for x in contact_list[1:3]]

        social_links = contact_info.getnext().xpath("a")
        for link in social_links:
            href = link.get("href").lower()
            plat, han = self.social_plat_and_hand_re.search(href).groups()
            for string in self.social_remove_regexes:
                han = string.sub("", han)
            legis.social_handles[plat] = han

        if legis.name == "Mike Gabbard":
            legis.social_handles["youtube"] = "senmikegabbard"


class CLIInterface:
    def __init__(self, legislature):
        self.legislature = legislature

    def start(self):
        print("Aloha and welcome to Hawaii State Legislator Search Tool!")
        print("Currently gathering information on Hawaii legislators...")
        self.legislature.process_list(display_progress_bar)
        print("\nLegislative data collected!")

        while True:
            chamber_input = get_chamber_input()
            chamber_selection = "House" if chamber_input == "H" else "Senate"
            district = get_district_input()
            self.display_legislator_info(chamber_selection, district)

            if not ask_for_another_district():
                break

        type_print("\nThank you for using the Hawaii State Legislator Search Tool.\n")
        time.sleep(1)
        customized_timing_message = get_time_of_day_greeting()
        type_print(f"Aloha, and {customized_timing_message}\n")
        time.sleep(1)
        sys.exit()

    def display_legislator_info(self, chamber_select, dist):
        legislator = self.legislature.members[chamber_select].get(str(dist))
        if legislator:
            type_print(f"\n{legislator.name} represents {chamber_select} "
                       f"District {dist}.\n")
            chamber_title = "Representative" if chamber_select == "House" else "Senator"
            type_print(
                f"Here is the information available on the {chamber_title}...\n\n")
            for key, value in legislator.__dict__.items():
                if key in {"chamber", "district", "state", "data_source"} or not value:
                    continue
                elif key == "social_handles":
                    for k, v in value.items():
                        type_print(f"{k.title()}: @{v}\n")
                else:
                    type_print(f"{key.title()}: {value}\n")
        else:
            type_print(f"\nNo legislator found for {chamber_select} District {dist}\n")


def display_progress_bar(current, total):
    bar_length = 50
    progress_length = int((current / total) * bar_length)
    bar = '█' * progress_length + '-' * (bar_length - progress_length)
    sys.stdout.write(f"\rProcessing: [{bar}] {current} of {total} legislators")
    sys.stdout.flush()


def type_print(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)


def get_district_input():
    while True:
        try:
            district_input = input(
                "Enter the number of the district you're interested in (e.g., '17'): ")
            return int(district_input)
        except ValueError:
            print("Please enter a valid numeric district number.")


def get_chamber_input():
    while True:
        chamber_input = input(
            "\nWould you like data on a member of the House or Senate? (H/S): ").upper()
        if chamber_input in ["H", "S"]:
            return chamber_input
        print("\nPlease enter valid input (H for House, S for Senate).")


def ask_for_another_district():
    while True:
        response = input("\nInterested in any other districts? (yes/no): ").lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'.")


def get_time_of_day_greeting():
    current_hour = datetime.datetime.now().hour
    if 3 <= current_hour < 12:
        return "have a great day!"
    elif 12 <= current_hour < 17:
        return "enjoy the rest of your day!"
    elif 17 <= current_hour < 22:
        return "have a great night!"
    else:
        return "stop looking up legislators in Hawaii, it's late! GET SOME SLEEP!"


if __name__ == "__main__":
    legislative_body = HawaiiLegislature()
    cli = CLIInterface(legislative_body)
    cli.start()
