import os
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from datetime import date, timedelta

dotenv.load_dotenv()

def subscribtion_checker():
    engine = create_engine(
        f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}'
        f'@{os.getenv("DB_HOST")}:5432/{os.getenv("DB_NAME")}',
        pool_pre_ping=True,
    )

    Base = automap_base()
    Base.prepare(engine, reflect=True)

    AvatarexUsers = Base.classes.avatarex_users
    AmoCRM = Base.classes.amocrm
    Subscriptions = Base.classes.subscriptions

    Session = sessionmaker(bind=engine)
    session = Session()

    for user in session.query(AvatarexUsers).all():
        print(f"Обработка пользователя: {user.email}")

        amocrm_entry = session.query(AmoCRM).filter(AmoCRM.user_id_id == user.id).first()
        if amocrm_entry:
            print(f"AmoCRM Хост: {amocrm_entry.host}")
        else:
            print("Запись AmoCRM для этого пользователя не найдена")

        active_subscription = False
        today = date.today()

        subscriptions = session.query(Subscriptions).filter(Subscriptions.user_id_id == user.id).all()
        if subscriptions:
            for subscription in subscriptions:
                end_date = subscription.start_date + timedelta(days=subscription.period)
                if today <= end_date:
                    active_subscription = True
                    days_left = (end_date - today).days
                    print(f"Подписка активна, осталось дней: {days_left}")
                else:
                    print("Подписка истекла")

            if not active_subscription:
                print("Все подписки истекли")
        else:
            print("Подписок для этого пользователя не найдено")

        print("-" * 40)

    session.close()


