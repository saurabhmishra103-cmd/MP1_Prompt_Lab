from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY : str
    OPENAI_BASE_URL : str = "https://openai.vocareum.com/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
    )

my_settings = Settings()

CANDIDATE_MODEL = 'gpt-4o-mini'
JUDGE_MODEL = 'gpt-4o'
TEMPERATURE = 0.0

RATES = {
    'gpt-4o-mini': {'in': 0.15 / 1_000_000, 'out': 0.6 / 1_000_000},
    'gpt-4o':      {'in': 2.50 / 1_000_000, 'out': 10.00 / 1_000_000}
}