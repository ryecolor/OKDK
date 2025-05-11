from django.db import migrations
from django.db.migrations.operations.special import SeparateDatabaseAndState

class Migration(migrations.Migration):
    dependencies = [
        ('alerts', '0002_weatherdata_delete_notification_delete_weatheralert'),
        ('drain', '0001_initial'),
        ('robot_info', '0001_initial'),
    ]

    operations = [
        # 1. 날씨 트리거
        SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    CREATE OR REPLACE FUNCTION notify_weather_change()
                    RETURNS trigger AS $$
                    BEGIN
                        PERFORM pg_notify('weather_change', json_build_object(
                            'forecast_type', NEW.forecast_type,
                            'precipitation_type', NEW.precipitation_type
                        )::text);
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    CREATE TRIGGER weather_data_change
                    AFTER UPDATE ON alerts_weatherdata
                    FOR EACH ROW WHEN (
                        OLD.precipitation_type IS DISTINCT FROM NEW.precipitation_type
                        AND NEW.precipitation_type != '없음'
                    )
                    EXECUTE FUNCTION notify_weather_change();
                    """,
                    reverse_sql="""
                    DROP TRIGGER IF EXISTS weather_data_change ON alerts_weatherdata;
                    DROP FUNCTION IF EXISTS notify_weather_change();
                    """
                )
            ]
        ),

        # 2. 배수구 트리거
        SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    CREATE OR REPLACE FUNCTION notify_drain_repair()
                    RETURNS trigger AS $$
                    BEGIN
                        PERFORM pg_notify('drain_repair_change', json_build_object(
                            'drain_id', NEW.drain_id,
                            'repair_result', NEW.repair_result
                        )::text);
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    CREATE TRIGGER drain_repair_change
                    AFTER INSERT ON drain_drainrepair
                    FOR EACH ROW
                    EXECUTE FUNCTION notify_drain_repair();
                    """,
                    reverse_sql="""
                    DROP TRIGGER IF EXISTS drain_repair_change ON drain_drainrepair;
                    DROP FUNCTION IF EXISTS notify_drain_repair();
                    """
                )
            ]
        ),

        # 3. 로봇 트리거
        SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    CREATE OR REPLACE FUNCTION notify_robot_repair()
                    RETURNS trigger AS $$
                    BEGIN
                        PERFORM pg_notify('robot_repair_change', json_build_object(
                            'robot_id', NEW.robot_id,
                            'repair_reason', NEW.repair_reason
                        )::text);
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    CREATE TRIGGER robot_repair_change
                    AFTER INSERT ON robot_info_robotrepair
                    FOR EACH ROW
                    EXECUTE FUNCTION notify_robot_repair();
                    """,
                    reverse_sql="""
                    DROP TRIGGER IF EXISTS robot_repair_change ON robot_info_robotrepair;
                    DROP FUNCTION IF EXISTS notify_robot_repair();
                    """
                )
            ]
        )
    ]
