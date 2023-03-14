import csv
from _operator import attrgetter
from itertools import chain

from django.http import HttpResponse

from stats.models import Match, Map


def export_Matches(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="matches.csv"'},
    )

    player = request.user.username

    # 3 queries with the name of active player
    p1_group = Match.objects.filter(player_1=player)
    p2_group = Match.objects.filter(player_2=player)
    p3_group = Match.objects.filter(player_3=player)

    # results are sorted by their id
    result_as_list = sorted(chain(p1_group, p2_group, p3_group), key=attrgetter("id"))

    model_fields_names = []
    fields = Match._meta.get_fields()
    for field in fields:
        field_data = field.name
        model_fields_names.append(field_data)

    writer = csv.writer(response)
    writer.writerow(model_fields_names)

    for match in result_as_list:
        fields = match._meta.get_fields()
        pure_values = []
        for field in fields:
            if field.many_to_one:
                # decodes foreing field relation, as value to string returns only an ID
                id = field.value_to_string(match)
                try:
                    a_value = field.related_model.objects.get(pk=id)
                except ValueError:
                    a_value = "None"
                except Map.DoesNotExist:
                    a_value = "Undefined"
            elif field.many_to_many:
                a_value = "+".join(
                    [item.name for item in field.value_from_object(match)]
                )
            else:
                a_value = field.value_to_string(match)
            pure_values.append(a_value)
        writer.writerow(pure_values)

    return response
