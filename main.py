from ai_qual import ai_qual
from db_ai_qual import db_ai_qual
from db_hard_qual import db_hard_qual
from hard_qual import hard_qual
from knowledge import knowledge
from prompt import prompt
from subscribtion_checker import subscribtion_checker


def main():
    subscribtion_checker()
    prompt()
    ai_qual()
    db_ai_qual()
    hard_qual()
    db_hard_qual()
    knowledge()

