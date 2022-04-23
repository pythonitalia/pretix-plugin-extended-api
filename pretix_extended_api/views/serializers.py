from pretix.api.serializers.i18n import I18nAwareModelSerializer
from pretix.api.serializers.item import ItemSerializer, QuestionSerializer
from pretix.base.models import OrderPosition, QuestionAnswer
from rest_framework import serializers


class EventBodySerializer(serializers.Serializer):
    organizer_slug = serializers.CharField(required=True)
    event_slug = serializers.CharField(required=True)


class AttendeeHasTicketBodySerializer(serializers.Serializer):
    attendee_email = serializers.EmailField(required=True)
    events = EventBodySerializer(many=True, required=True)


class AttendeeTicketBodySerializer(serializers.Serializer):
    attendee_email = serializers.EmailField(required=True)
    events = EventBodySerializer(many=True, required=False)



class AnswerSerializer(I18nAwareModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = QuestionAnswer
        fields = ("question", "answer", "options")


class OrderPositionSerializer(I18nAwareModelSerializer):
    answers = AnswerSerializer(many=True)
    attendee_name = serializers.CharField(required=False)

    class Meta:
        model = OrderPosition
        fields = (
            "addon_to",
            "answers",
            "attendee_email",
            "attendee_name",
            "attendee_name_parts",
            "canceled",
            "city",
            "company",
            "id",
            "positionid",
            "price",
            "pseudonymization_id",
            "secret",
            "state",
            "street",
            "subevent",
            "tax_rate",
            "tax_rule",
            "tax_value",
            "variation",
            "voucher",
            "zipcode",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["item"] = ItemSerializer(read_only=True, context=self.context)
