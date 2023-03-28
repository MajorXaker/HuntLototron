import csv
import datetime
import hashlib
import re

from django.contrib.auth.models import User

from stats.models import AmmoType, Player, Map

# from numpy import mat
from stats.models import Match, Compound, Weapon


class AuxClass:
    @staticmethod
    def credentials_to_dict(url_request, debug=False):
        """Exports usable data on current logged user

        'anonymous': is_anon,
        'has_aka': has_aka,
        'username': username,
        'playername': playername,
        'credentials': (username, playername),
        'name' : aka or username
        'user' : userclass of active user
        """
        username = url_request.user.username
        user = {
            "username": username,
        }

        try:
            playername = url_request.user.username_of_player.also_known_as
            has_aka = True if playername != "" else False

        except AttributeError:
            playername = None
            has_aka = False

        name = playername if has_aka else username

        is_anon = True if username == "" else False

        user = {
            "anonymous": is_anon,
            "has_aka": has_aka,
            "username": username,
            "playername": playername,
            "credentials": (username, playername),
            "name": name,
            "user": url_request.user,
        }

        if debug:
            print(user)

        return user


class DjangoDatetime:
    def __init__(self) -> None:
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.year = 0
        self.month = 0
        self.day = 0

    def date_cleanup(self, date):
        """Function takes string date and recompiles it to be usable by django
        usually returns a datetime class
        as_text - returns string containing date
        fake_class - returns an artificially constructed class to satisfy django's demands
        """
        patterns = [  # 0) 1-12-1963
            r"(\d{1,2})-(\d{1,2})-(\d{4})$",
            # 1) 1789-7-14
            r"(\d{4})-(\d{1,2})-(\d{1,2})$",
            # 2) 1.12.1963
            r"(\d{1,2}).(\d{1,2}).(\d{4})$",
            # 3) 1789.7.14
            r"(\d{4}).(\d{1,2}).(\d{1,2})$",
        ]

        try:
            res = str(int(date))
        except ValueError:
            pass

        for pat in patterns:
            q = re.match(pat, date)
            if q:
                # 0) 1-12-1963
                if pat == patterns[0]:
                    year = re.sub(patterns[0], r"\3", date)
                    month = re.sub(patterns[0], r"\2", date)
                    day = re.sub(patterns[0], r"\1", date)
                    res = "{0}-{1:0>2}-{2:0>2}".format(year, month, day)
                # 1) 1789-7-14
                if pat == patterns[1]:
                    year = re.sub(patterns[1], r"\1", date)
                    month = re.sub(patterns[1], r"\2", date)
                    day = re.sub(patterns[1], r"\3", date)
                    res = "{0}-{1:0>2}-{2:0>2}".format(year, month, day)
                # 2) '1945-2'
                if pat == patterns[2]:
                    year = re.sub(patterns[2], r"\3", date)
                    month = re.sub(patterns[2], r"\2", date)
                    day = re.sub(patterns[2], r"\1", date)
                    res = "{0}-{1:0>2}-{2:0>2}".format(year, month, day)
                # 1) 1789-7-14
                if pat == patterns[3]:
                    year = re.sub(patterns[3], r"\1", date)
                    month = re.sub(patterns[3], r"\2", date)
                    day = re.sub(patterns[3], r"\3", date)
                    res = "{0}-{1:0>2}-{2:0>2}".format(year, month, day)
                else:
                    res = date
        self.res = res
        self.day = day
        self.month = month
        self.year = year

        # class FakeClass():
        #     def __init__(self, year = 0, month = 0, day = 0, minutes = 0, seconds = 0) -> None:

        # self.minutes = minutes
        # self.seconds = seconds

        # def __str__(self) -> str:
        #     return f"{self.year}-{self.month}-{self.day}"

    def time_cleanup(self, time: str):
        data = time.split(":")

        self.hours = int(data[0])
        self.minutes = int(data[1])
        self.seconds = int(data[2])

    def get_class_date(self):
        return datetime.date(int(self.year), int(self.month), int(self.day))

    def get_text_date(self):
        return self.res

    def get_class_time(self):
        # d_class = datetime.datetime(
        #     year = 1,
        #     month = 1,
        #     day = 1,
        #     hour = int(self.hours),
        #     minute = int(self.minutes),
        #     second = int(self.seconds)
        #     )
        self.days = 1
        self.microseconds = 1
        return self

    def get_text_time(self):
        return f"{self.hours}:{self.minutes}:{self.seconds}"
        # A combination of a date and a time. Attributes: year, month, day, hour, minute, second, microsecond,

        # if mode == '':
        # elif mode == 'fake_class_date':
        #     return FakeClass(int(year), int(month), int(day))
        # elif mode == 'fake_class_duration':
        #     return FakeClass(int(year), int(month), int(day))
        # else:


class MatchesDecoder:
    class ImportedMatch:
        fields = [
            "wl_status",
            "date",
            "kills_total",
            "playtime",
            "map",
            "player_1",
            "player_1_primary_weapon",
            "player_1_primary_ammo_A",
            "player_1_primary_ammo_B",
            "player_1_secondary_weapon",
            "player_1_secondary_ammo_A",
            "player_1_secondary_ammo_B",
            "player_1_kills",
            "player_1_assists",
            "player_1_deaths",
            "player_1_bounty",
            "player_2",
            "player_2_primary_weapon",
            "player_2_primary_ammo_A",
            "player_2_primary_ammo_B",
            "player_2_secondary_weapon",
            "player_2_secondary_ammo_A",
            "player_2_secondary_ammo_B",
            "player_2_kills",
            "player_2_assists",
            "player_2_deaths",
            "player_2_bounty",
            "player_3",
            "player_3_primary_weapon",
            "player_3_primary_ammo_A",
            "player_3_primary_ammo_B",
            "player_3_secondary_weapon",
            "player_3_secondary_ammo_A",
            "player_3_secondary_ammo_B",
            "player_3_kills",
            "player_3_assists",
            "player_3_deaths",
            "player_3_bounty",
            "fights_locations",
        ]

        players_weapon_fields = [
            "primary_weapon",
            "primary_ammo_A",
            "primary_ammo_B",
            "secondary_weapon",
            "secondary_ammo_A",
            "secondary_ammo_B",
        ]

        players = ["player_1", "player_2", "player_3"]

        special_fields = ["date", "playtime"]

        digital_fields = [
            "player_1_kills",
            "player_1_assists",
            "player_1_deaths",
            "player_1_bounty",
            "player_2_kills",
            "player_2_assists",
            "player_2_deaths",
            "player_2_bounty",
            "player_3_kills",
            "player_3_assists",
            "player_3_deaths",
            "player_3_bounty",
            "kills_total",
        ]

        class IncorrectCSVValueException(Exception):
            """Exception is raised, when CVS handler encounters an incorrect value in a match, this stops match import

            Atributes
            field - name of field which is faulty
            message - message to tell user
            """

            def __init__(
                self,
                field="-field-",
                field_type="-field_type-",
                message="is invalid",
                super_message=None,
                *args: object,
            ) -> None:
                super().__init__(*args)
                if super_message == None:
                    self.message = f"The {field_type} with name {field} {message}."
                else:
                    self.message = message

        def __init__(self, matchData: list, player_owner: Player, line_number) -> None:
            """
            Atributes
            matchData"""
            self.raw_data = matchData.copy()
            self.faulty_match = False  # used to stop processing this match
            self.messages = []  # log messages, first entry is row number
            self.good_data = {}
            self.player_owner = player_owner
            # TODO verifyers and relation makers
            # TODO limitations for matches qty
            # TODO pass data to model

            self.messages.append(f"Line {line_number}:")

        def __str__(self) -> str:
            return str(self.good_data)

        def match_fail(self, message="Match import failed.", fail=True):
            self.faulty_match = True if fail else False
            self.messages.append(message)

        def normalise(self):
            for field in self.digital_fields:
                if self.faulty_match:
                    # this will skip working with fields when critical problem is encountered
                    break

                try:
                    # if field is not found or it's faulty - put 0
                    value = int(self.raw_data.get(field, 0))
                    if value < 0:
                        raise self.IncorrectCSVValueException(
                            field=field,
                            field_type="digit field",
                            problem="can't be negative",
                        )

                    if value > 50 and "bounty" not in field:
                        raise self.IncorrectCSVValueException(
                            field=field,
                            field_type="digit field",
                            problem="can't be over 50",
                        )

                    if field == "total_kills":
                        if (
                            self.good_data["player_1_kills"]
                            + self.good_data["player_1_kills"]
                            + self.good_data["player_1_kills"]
                            > value
                        ):
                            value = (
                                self.good_data["player_1_kills"]
                                + self.good_data["player_1_kills"]
                                + self.good_data["player_1_kills"]
                            )
                            self.messages.append(
                                "Total kills corrected, was less than sum of player kills."
                            )
                    self.good_data[field] = value

                except self.IncorrectCSVValueException as e:
                    self.match_fail(e)

            for player in self.players:
                if self.faulty_match:
                    # this will skip working with fields when critical problem is encountered
                    break
                # 'player id'
                if player == "player_1":
                    self.good_data[player] = self.player_owner
                    playername = self.player_owner.also_known_as
                else:
                    try:
                        playername = self.raw_data[player]
                    except KeyError:
                        self.good_data[player] = None
                        playername = None

                    if playername == None or playername == "None":
                        self.match_fail(
                            f'"{player}" is set as "None", setting all his fields to None.',
                            fail=False,
                        )
                        self.good_data[player] = None
                    else:
                        try:
                            self.good_data[player] = Player.objects.get(
                                also_known_as=playername
                            )
                        except Player.DoesNotExist:
                            try:
                                self.good_data[player] = User.objects.get(
                                    username=playername
                                ).username
                            except User.DoesNotExist:
                                self.match_fail(
                                    f'Player "{playername}" of column "{player}" is not found.'
                                )

                # p = self.good_data[player]
                # assert isinstance(p, Player) or p is None

                for field in self.players_weapon_fields:
                    fieldname = "_".join((player, field))
                    try:
                        lookup_class = Weapon if "weapon" in field else AmmoType
                        if playername == None or playername == "None":
                            self.good_data[fieldname] = None
                        else:
                            self.good_data[fieldname] = lookup_class.objects.get(
                                name=self.raw_data[fieldname]
                            )
                    except (Weapon.DoesNotExist, AmmoType.DoesNotExist):
                        self.match_fail(
                            f'Incorrect value: "{self.raw_data[fieldname]}" from column "{fieldname}", "Unknown" is used instead.',
                            fail=False,
                        )
                    except KeyError:
                        self.match_fail(
                            f'No column "{fieldname}" provided, "Unknown" is used instead.',
                            fail=False,
                        )

            if not self.faulty_match:
                try:
                    self.good_data["map"] = Map.objects.get(name=self.raw_data["map"])
                except Map.DoesNotExist:
                    self.match_fail(
                        f'Map {self.raw_data["map"]} does not existust, using "Unknown map".',
                        fail=False,
                    )
                    self.good_data["map"] = Map.objects.get(name="Unknown")
                except KeyError:
                    self.match_fail(
                        f'Field "map" is missing, using "Unknown map"', fail=False
                    )
                    self.good_data["map"] = Map.objects.get(name="Unknown")

                self.good_data["fights_locations"] = []
                try:
                    places = self.raw_data["fights_locations"]
                    locations = places.split("+")
                    for location_name in locations:
                        try:
                            location = Compound.objects.get(name=location_name)
                        except Compound.DoesNotExist:
                            self.match_fail(
                                f'Compound "{location_name}" does not exist."',
                                fail=False,
                            )
                        else:
                            self.good_data["fights_locations"].append(location)

                except KeyError:
                    self.messages.append("No fights locations found in a CSV file.")

                for field in ["playtime", "date", "wl_status"]:
                    try:
                        if field == "date":
                            temp_date = self.raw_data[field]
                            # formatted_date = AuxClass.date_cleanup(temp_date, mode = 'fake_class_date')
                            date = DjangoDatetime()
                            date.date_cleanup(temp_date)
                            self.good_data[field] = date.get_class_date()
                        elif field == "playtime":
                            temp_time = self.raw_data[field]
                            time = DjangoDatetime()
                            time.time_cleanup(time=temp_time)
                            self.good_data[field] = time.get_class_time()
                            # formatted_date = AuxClass.date_cleanup(temp_date, mode = 'fake_class_duration')
                            # self.good_data[field] = formatted_date
                        else:
                            self.good_data[field] = self.raw_data[field]
                    except KeyError:
                        self.match_fail(f'No "{field}" provided.')

                self.good_data["imported_match"] = True

            if self.faulty_match:
                self.messages.append("Match processing stopped.")
            else:
                self.messages.append("Match processing complete.")

        def get_md5(self) -> str:
            values = [
                self.good_data["date"],
                self.good_data["playtime"],
                self.good_data["map"],
                self.good_data["player_1"],
                self.good_data["player_2"],
                self.good_data["player_3"],
                self.good_data["player_1_bounty"],
                self.good_data["player_2_bounty"],
                self.good_data["player_3_bounty"],
                self.good_data["player_1_primary_weapon"],
                self.good_data["player_1_secondary_weapon"],
                self.good_data["fights_locations"],
            ]
            str_values = [str(val) for val in values]
            hashable_str = bytes("".join(str_values), encoding="utf-8")
            hashed = hashlib.md5()
            hashed.update(hashable_str)
            encoded = hashed.hexdigest()
            return encoded

    def __init__(
        self,
        csv_file,
        player_owner: Player,
        delimeter=",",
    ) -> None:
        reader = csv.DictReader(csv_file, delimiter=delimeter)
        self.data = []
        for match in reader:
            self.data.append(
                self.ImportedMatch(
                    match, player_owner=player_owner, line_number=reader.line_num
                )
            )

    def __getitem__(self, index):
        return self.data[index]

    def normalise(self):
        self.messages = []
        for match in self.data:
            match.normalise()
            self.messages.append(" | ".join(match.messages))

    def transfer(self):
        mathes_hashed = [match.get_md5() for match in Match.objects.all()]

        allowed_matches = {}
        for match in self.data:
            if match.faulty_match == False:
                match_md5 = match.get_md5()
                match_index = self.data.index(match)
                if match_md5 in mathes_hashed:
                    self.messages.append(
                        f"Match {match_index} already exists. This match will be discarded."
                    )
                else:
                    if match_md5 in allowed_matches:
                        self.messages.append(
                            f"Duplication of {match_index} found. Second instance will be discarded."
                        )
                    else:
                        allowed_matches[match_md5] = match
                allowed_matches[match_md5] = match

        # print(allowed_matches)
        for md5, processed_match in allowed_matches.items():
            db_match = Match(
                wl_status=processed_match.good_data["wl_status"],
                date=processed_match.good_data["date"],
                kills_total=processed_match.good_data["kills_total"],
                playtime=processed_match.good_data["playtime"],
                map=processed_match.good_data["map"],
                player_1=processed_match.good_data["player_1"],
                player_1_primary_weapon=processed_match.good_data[
                    "player_1_primary_weapon"
                ],
                player_1_primary_ammo_A=processed_match.good_data[
                    "player_1_primary_ammo_A"
                ],
                player_1_primary_ammo_B=processed_match.good_data[
                    "player_1_primary_ammo_B"
                ],
                player_1_secondary_weapon=processed_match.good_data[
                    "player_1_secondary_weapon"
                ],
                player_1_secondary_ammo_A=processed_match.good_data[
                    "player_1_secondary_ammo_A"
                ],
                player_1_secondary_ammo_B=processed_match.good_data[
                    "player_1_secondary_ammo_B"
                ],
                player_1_kills=processed_match.good_data["player_1_kills"],
                player_1_assists=processed_match.good_data["player_1_assists"],
                player_1_deaths=processed_match.good_data["player_1_deaths"],
                player_1_bounty=processed_match.good_data["player_1_bounty"],
                player_2=processed_match.good_data["player_2"],
                player_2_primary_weapon=processed_match.good_data[
                    "player_2_primary_weapon"
                ],
                player_2_primary_ammo_A=processed_match.good_data[
                    "player_2_primary_ammo_A"
                ],
                player_2_primary_ammo_B=processed_match.good_data[
                    "player_2_primary_ammo_B"
                ],
                player_2_secondary_weapon=processed_match.good_data[
                    "player_2_secondary_weapon"
                ],
                player_2_secondary_ammo_A=processed_match.good_data[
                    "player_2_secondary_ammo_A"
                ],
                player_2_secondary_ammo_B=processed_match.good_data[
                    "player_2_secondary_ammo_B"
                ],
                player_2_kills=processed_match.good_data["player_2_kills"],
                player_2_assists=processed_match.good_data["player_2_assists"],
                player_2_deaths=processed_match.good_data["player_2_deaths"],
                player_2_bounty=processed_match.good_data["player_2_bounty"],
                player_3=processed_match.good_data["player_3"],
                player_3_primary_weapon=processed_match.good_data[
                    "player_3_primary_weapon"
                ],
                player_3_primary_ammo_A=processed_match.good_data[
                    "player_3_primary_ammo_A"
                ],
                player_3_primary_ammo_B=processed_match.good_data[
                    "player_3_primary_ammo_B"
                ],
                player_3_secondary_weapon=processed_match.good_data[
                    "player_3_secondary_weapon"
                ],
                player_3_secondary_ammo_A=processed_match.good_data[
                    "player_3_secondary_ammo_A"
                ],
                player_3_secondary_ammo_B=processed_match.good_data[
                    "player_3_secondary_ammo_B"
                ],
                player_3_kills=processed_match.good_data["player_3_kills"],
                player_3_assists=processed_match.good_data["player_3_assists"],
                player_3_deaths=processed_match.good_data["player_3_deaths"],
                player_3_bounty=processed_match.good_data["player_3_bounty"],
                external=True
                # fights_locations = processed_match.good_data["fights_locations"]
            )
            db_match.save()

            for location in processed_match.good_data["fights_locations"]:
                db_match.fights_locations.add(location)

            # print(processed_match.good_data["fights_locations"])
            # comp = Compound.objects.get(name='Maw Battery')
            # print(processed_match.good_data["fights_locations"][0] == comp)

            # # db_match.fights_locations.add(processed_match.good_data["fights_locations"])
            # # print(db_match)
