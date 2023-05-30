from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from events.models import Calendar, Event, ShareTheCalendar


class CalendarSerializer(serializers.ModelSerializer):
    """
    Сериализатор календаря.
    Поле public исключено из выдачи.
    """

    owner = serializers.SlugRelatedField(read_only=True, slug_field='email')

    class Meta:
        model = Calendar
        fields = (
            'id',
            'name',
            'description',
            'owner',
            'color',
        )
        extra_kwargs = {
            'name':
                {'required': True, 'error_messages':
                    {'required': 'Не задано название календаря',
                     'null': 'Название не может быть null',
                     }
                 },
        }

    @transaction.atomic
    def create(self, validated_data):
        """
        При POST запросе на создание экземпляра модели Calendar
        поле owner автоматически заполняется текущим аутентифицированным
        пользователем.
        """

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
            return super().create(validated_data)
        raise serializers.ValidationError(
            'Пользователь не аутентифицирован.')


class ShortCalendarSerializer(serializers.ModelSerializer):
    """
    Сериализатор с укороченным представлением. Необходим для передачи в
    эвенте только необходимых данных, вложенным сериализатором.
    """

    class Meta:
        model = Calendar
        fields = (
            'id',
            'name',
            'color',
        )


class ReadEventSerializer(serializers.ModelSerializer):
    calendar = ShortCalendarSerializer(read_only=True)
    datetime_start = serializers.DateTimeField(format='%Y-%m-%dT%H:%M')
    datetime_finish = serializers.DateTimeField(format='%Y-%m-%dT%H:%M')

    class Meta:
        model = Event
        fields = (
            'id',
            'datetime_start',
            'datetime_finish',
            'all_day',
            'name',
            'description',
            'day_off',
            'holiday',
            'calendar',
        )


class WriteEventSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи данных.
    В extra_kwargs изменены стандартные ошибки DRF на кастомные.
    """

    class Meta:
        model = Event
        fields = (
            'id',
            'datetime_start',
            'datetime_finish',
            'all_day',
            'name',
            'description',
            'day_off',
            'holiday',
            'calendar',
        )
        extra_kwargs = {
            'datetime_start':
                {'required': True, 'error_messages':
                    {'required': 'Дата начала мероприятия отсутствует',
                     'invalid': 'Неправильный формат даты и времени',
                     'null': 'Дата начала мероприятия не может быть null',
                     }
                 },
            'datetime_finish':
                {'required': True, 'error_messages':
                    {'required': 'Дата завершения мероприятия отсутствует',
                     'invalid': 'Неправильный формат даты и времени',
                     'null': 'Дата завершения мероприятия не может быть null',
                     }
                 },
            'calendar':
                {'required': True, 'error_messages':
                    {'required': 'Не выбран календарь',
                     'invalid': 'Укажите id календаря',
                     'null': 'Календарь не может быть null',
                     }
                 },
            'all_day':
                {'required': False, 'error_messages':
                    {'invalid': 'Флаг all_day должен быть True или False'}
                 }
        }

    def to_representation(self, instance):
        """
        Метод переопределяет сериализатор для отображения после
        успешного запроса на изменение данных
        """

        return ReadEventSerializer(
            instance=instance, context=self.context).data

    def set_event_date(self, validated_data):
        """
        Метод для установки времени начала и завершения мероприятия, если
        флаг all_day установлен.
        """

        keys = ('all_day', 'datetime_start', 'datetime_finish')
        all_day, start, finish = [validated_data.get(key) for key in keys]
        if all_day:
            validated_data['datetime_start'] = start.replace(
                hour=0, minute=0
            )
            validated_data['datetime_finish'] = finish.replace(
                hour=23, minute=59, second=59,
            )
        return validated_data

    def create(self, validated_data):
        validated_data = self.set_event_date(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        params = {
            'all_day': instance.all_day,
            'datetime_start': instance.datetime_start,
            'datetime_finish': instance.datetime_finish,
        }
        for key, value in params.items():
            if validated_data.get(key) is None:
                validated_data[key] = value

        validated_data = self.set_event_date(validated_data)
        return super().update(instance, validated_data)

    def validate(self, data):
        calendar = data.get('calendar')
        user = self.context.get('request').user
        if calendar and user != calendar.owner:
            raise ValidationError(
                {'calendar': 'Можно использовать только свой календарь'}
            )
        event = self.instance
        datetime_start = data.get('datetime_start') or event.datetime_start
        datetime_finish = data.get('datetime_finish') or event.datetime_finish

        if datetime_start > datetime_finish:
            message = 'Мероприятие не может начинаться после даты окончания.'
            raise serializers.ValidationError(message)

        return data


class ShareTheCalendarSerializer(serializers.ModelSerializer):
    """
    Сериализация данных шеринга календаря.
    Owner - владелец календаря.
    user (share_to) - пользователь которому предоставляется доступ.
    calendar - календарь, которым делится владелец.

    Создание:
    При создании записи в бд owner и calendar подставляются автоматически и
    являются текущим календарем и текущим пользователем.

    Валидация:
    1. owner != user
    2. Поля user и calendar уникальные
    3. calendar является календарем созданным owner'ом
    """
    owner = serializers.SlugRelatedField(read_only=True, slug_field='email')
    calendar = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = ShareTheCalendar
        fields = (
            'owner',
            'user',
            'calendar',
        )

    # def create(self, validated_data):
    # todo не пойму почему, но этот метод не вызывается. Пытался дебажить
    #  но сюда так и не дошли операции.
    #
    #     request = self.context.get('request')
    #     calendar_id = self.context['request'].parser_context['kwargs'].get(
    #         'id')
    #     calendar = get_object_or_404(Calendar, id=calendar_id)
    #
    #     if request and request.user.is_authenticated:
    #         validated_data['owner'] = request.user
    #         validated_data['calendar'] = calendar
    #         instance = super().create(validated_data)
    #         return instance
    #     raise serializers.ValidationError(
    #         'Пользователь не аутентифицирован.')
