from django.db import models


class Organization(models.Model):
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    organization_name = models.CharField(max_length=300,
                                         verbose_name='Организация')

    def __str__(self):
        return self.organization_name


class TgUser(models.Model):
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    BASIC = "BS"
    ADMIN = "AD"

    USER_ROLE = [
        (BASIC, "Basic"),
        (ADMIN, "Admin"),
    ]

    user_role = models.CharField(
        max_length=2,
        choices=USER_ROLE,
        default=BASIC,
    )

    tg_id = models.PositiveIntegerField(default=0,
                                        blank=True,
                                        verbose_name='ID пользователя в телеграм'
                                        )

    user_photo = models.ImageField(blank=True,
                                   upload_to='tgbot/images/',
                                   verbose_name='Фото'
                                   )

    full_name = models.CharField(max_length=300,
                                 blank=True,
                                 verbose_name='ФИО сотрудника'
                                 )

    user_organization = models.ForeignKey(Organization,
                                          on_delete=models.PROTECT,
                                          verbose_name='Организация'
                                          )

    job_title = models.CharField(max_length=200,
                                 blank=True,
                                 verbose_name='Должность сотрудника'
                                 )

    phone_number = models.CharField(max_length=20,
                                    blank=True,
                                    verbose_name='Номер телефона'
                                    )

    phone_number_work = models.CharField(max_length=20,
                                         blank=True,
                                         verbose_name='Рабочий номер телефона'
                                         )

    email_address = models.CharField(max_length=200,
                                     blank=True,
                                     verbose_name='e-mail'
                                     )

    nick_name = models.CharField(max_length=200,
                                 blank=True,
                                 verbose_name='Никнейм в телеграм')

    description = models.TextField(blank=True,
                                   verbose_name='Описание'
                                   )

    def __str__(self):
        return self.full_name
