import os
import json
import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

dotenv.load_dotenv()


def ai_qual():
    engine = create_engine(
        f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}'
        f'@{os.getenv("DB_HOST")}:5432/{os.getenv("DB_NAME")}',
        pool_pre_ping=True,
    )

    Base = automap_base()
    Base.prepare(engine, reflect=True)

    Settings = Base.classes.settings
    PromptSettings = Base.classes.prompt_settings
    Pipelines = Base.classes.pipelines
    Statuses = Base.classes.statuses
    AvatarExUsers = Base.classes.avatarex_users
    OpenAIModels = Base.classes.openai_models
    Qualifications = Base.classes.qualification

    Session = sessionmaker(bind=engine)
    session = Session()

    settings_records = session.query(Settings).filter(
        Settings.mode_id == 9,
    ).all()

    json_data_list = []
    counter = 0

    for setting in settings_records:
        counter += 1
        prompt_setting = session.query(PromptSettings).filter_by(id=setting.prompt_settings_id).first()
        model_title = session.query(OpenAIModels.title).filter_by(id=setting.model_id).scalar()

        qualification = session.query(Qualifications).filter_by(id=setting.qualification_id_id).first()

        if qualification and qualification.questions:
            enabled_fields_formatted = [
                {
                    "crmFieldId": int(field.get("amo_id", 0)),
                    "question": field.get("message", "")
                }
                for field in qualification.questions
                if field.get("enabled", False)
            ]
        else:
            enabled_fields_formatted = []

        json_data = {
            "name": setting.name,
            "contextSettings": {
                "prompt": prompt_setting.context,
                "tokens": prompt_setting.max_tokens,
                "temperature": prompt_setting.temperature,
            },
            "paymentSettings": {
                "isOurTokensStatus": False,
                "openaiApiKey": session.query(AvatarExUsers).filter_by(id=setting.user_id_id).first().openai_api_key,
                "gptmodel": model_title if model_title else "default-model",
            },
            "stagesAndStatusesSettings": {
                "enabledPipelineId": setting.pipeline_id_id,
                "enabledStatusesIds": ','.join(
                    str(status.id) for status in session.query(Statuses).all() if status.user_id_id == setting.user_id_id),
            },
            "additionalSettings": {
                "workByTimeStatus": setting.is_date_work_active,
                "workByTimeStart": setting.datetimeValueStart,
                "workByTimeEnd": setting.datetimeValueFinish,
                "deactivateAvatarIfInterventionStatus": setting.is_manager_intervented_active,
                "interventionDeactivationTime": setting.interventedtimeValue,
                "delayMessageProcessingStatus": setting.checkbox_processing_new_message,
                "messageProcessingDelayTime": setting.new_message_processing_time,
                "processImagesStatus": True,
                "processVoiceMessagesStatus": setting.voice_detection,
            },
            "qualificationSettings": {
                "enabledFields": enabled_fields_formatted,
                "afterQualificationMessage": qualification.finish_message if qualification else "Default message",
                "afterQualificationRedirectStageId": setting.qualification_redirect_select,
                "triggerPhrases": setting.trigger_phrases,
                "redirectMessage": setting.qualification_redirect_message,
                "repeatMessage": setting.qualification_repeat_message
            }
        }

        json_data_list.append(json_data)

    json_output = json.dumps(json_data_list, indent=4, ensure_ascii=False)

    output_dir = 'json'
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, 'ai_qual.json')

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json_output)

    session.close()

    print(f"Обработано {counter} настроек AI Qual")
