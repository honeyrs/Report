from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonFake,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonIllegalDrugs,
    InputReportReasonPersonalDetails,
    InputReportReasonOther
)
import time
import sys
import os
from termcolor import colored

# Function to clear the session file if it exists
def clear_session_file(session_file):
    if os.path.exists(session_file):
        os.remove(session_file)

# API credentials
api_id = input(colored("Enter your API ID: ", "yellow"))
api_hash = input(colored("Enter your API Hash: ", "yellow"))

# Option to input string session manually or let user log in
string_session = input(colored("Enter your String Session (leave empty to login again): ", "yellow"))

# Session file name
session_file = 'report_session.session'

# Remove the session file to force a fresh session
clear_session_file(session_file)

# Define report reasons
report_reasons = {
    1: ("I don't like it", InputReportReasonOther()),
    2: ("Child abuse", InputReportReasonChildAbuse()),
    3: ("Violence", InputReportReasonViolence()),
    4: ("Illegal goods", InputReportReasonIllegalDrugs()),
    5: ("Illegal adult content", InputReportReasonPornography()),
    6: ("Personal data", InputReportReasonPersonalDetails()),
    7: ("Terrorism", InputReportReasonViolence()),
    8: ("Scam or spam", InputReportReasonSpam()),
    9: ("Copyright", InputReportReasonCopyright()),
    10: ("Other", InputReportReasonOther())
}

def check_exit(input_value):
    if input_value.lower() == "exit":
        print(colored("Exiting the script.", "red"))
        sys.exit()

def check_home(input_value):
    return input_value.lower() == "home"

def get_valid_input(prompt, valid_options=None):
    while True:
        user_input = input(colored(prompt, "red"))
        check_exit(user_input)
        if check_home(user_input):
            return "home"
        if valid_options:
            try:
                user_input = int(user_input)
                if user_input in valid_options:
                    return user_input
                else:
                    print(colored(f"Please select a valid option from {valid_options}.", "red"))
            except ValueError:
                print(colored("Invalid input. Please enter a number.", "red"))
        else:
            return user_input

def get_valid_integer_input(prompt):
    while True:
        user_input = input(colored(prompt, "red"))
        check_exit(user_input)
        if check_home(user_input):
            return "home"
        try:
            return int(user_input)
        except ValueError:
            print(colored("Invalid input. Please enter a valid integer.", "red"))

async def report_entity(client):
    while True:
        print(colored("1: Account\n2: Channel\n3: Group\n4: Bot\n5: Post Link (Channel/Group Only)", "green"))
        report_type = get_valid_input("What you want to report: ", valid_options=[1, 2, 3, 4, 5])
        
        if report_type == "home":
            continue
        
        print()

        if report_type == 5:
            while True:
                post_link = input(colored("Enter the full post link (e.g., https://t.me/channel/12345): ", "red"))
                check_exit(post_link)
                if check_home(post_link):
                    break
                print()

                if not post_link.startswith("https://t.me/"):
                    print(colored("You can only report a post link. Please provide a valid link.\n", "red"))
                    continue

                try:
                    parts = post_link.replace("https://t.me/", "").split("/")
                    if len(parts) != 2 or not parts[1].isdigit():
                        print(colored("Invalid post link format. Please provide a valid link.\n", "red"))
                        continue

                    channel_username = parts[0]
                    message_id = int(parts[1])

                    channel = await client.get_entity(channel_username)

                    print(colored("\nReasons:", "green"))
                    for number, (reason_name, _) in report_reasons.items():
                        print(f"{number}: {reason_name}")
                    print()

                    reason_choice = get_valid_input(colored("Enter the number for the reason: ", "red"), valid_options=report_reasons.keys())
                    if reason_choice == "home":
                        break

                    print()

                    num_reports = get_valid_integer_input(colored("How many reports to submit? ", "red"))
                    if num_reports == "home":
                        break

                    print()

                    for i in range(num_reports):
                        await client(ReportPeerRequest(
                            peer=channel,
                            reason=report_reasons[reason_choice][1],
                            message=f"Reported post ID {message_id} for {report_reasons[reason_choice][0]}"
                        ))
                        print(colored(f"Report {i + 1} submitted.", "green"))
                        time.sleep(2)

                    print(colored("\nAll reports sent successfully.", "green"))
                    break
                except Exception as e:
                    print(colored(f"Error retrieving entity: {e}\n", "red"))
                    continue

        else:
            entity_username = input(colored("Enter the username or ID (e.g., @username): ", "red"))
            check_exit(entity_username)
            if check_home(entity_username):
                break
            print()

            if not entity_username.startswith("@"):
                entity_username = "@" + entity_username
            
            try:
                entity = await client.get_entity(entity_username)
            except Exception as e:
                print(colored(f"Error retrieving entity: {e}\n", "red"))
                continue

            print(colored("\nReasons:", "green"))
            for number, (reason_name, _) in report_reasons.items():
                print(f"{number}: {reason_name}")
            print()
            
            reason_choice = get_valid_input(colored("Enter the number for the reason: ", "red"), valid_options=report_reasons.keys())
            if reason_choice == "home":
                continue

            print()
            
            num_reports = get_valid_integer_input(colored("How many reports to submit? ", "red"))
            if num_reports == "home":
                continue

            print()
            
            try:
                for i in range(num_reports):
                    await client(ReportPeerRequest(peer=entity, reason=report_reasons[reason_choice][1], message=f"Reported for {report_reasons[reason_choice][0]}"))
                    print(colored(f"[ Report {i + 1} successfully submitted. ]", "green"))
                    time.sleep(2)
                print(colored("\nAll reports sent successfully.", "green"))
            finally:
                await client.disconnect()

        sys.exit()

def main():
    # Ask for String Session if not provided earlier
    if not string_session:
        print(colored("Logging in... please follow the prompts for authentication.", "yellow"))
        client = TelegramClient(session_file, api_id, api_hash)
        client.start()
        string_session = client.session.save()  # Save string session after login
        print(colored(f"Your String Session: {string_session}", "yellow"))
    else:
        client = TelegramClient(session_file, api_id, api_hash, string_session=string_session)
        client.connect()

    client.loop.run_until_complete(report_entity(client))

if __name__ == "__main__":
    main()
