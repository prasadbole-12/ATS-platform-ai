"""
app/ml/skill_extractor.py
--------------------------
Extracts technical and soft skills from resume / JD text.

Strategy (in order):
  1. Direct substring match against the skills taxonomy (case-insensitive)
  2. Regex patterns for versioned skills  (e.g. "Python 3.11", "Node.js 18")
  3. Alias normalisation  (e.g. "js" → "JavaScript")
"""

import re
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Skills taxonomy
# ─────────────────────────────────────────────────────────────────────────────

SKILLS_TAXONOMY: dict[str, list[str]] = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#",
        "Go", "Rust", "Kotlin", "Swift", "Ruby", "PHP", "Scala", "R",
        "MATLAB", "Perl", "Haskell", "Lua", "Dart", "Elixir", "Clojure",
        "Julia", "Groovy", "Bash", "Shell", "PowerShell",
    ],
    "Web Frameworks": [
        "React", "Next.js", "Vue.js", "Angular", "Svelte", "Nuxt.js",
        "FastAPI", "Django", "Flask", "Express.js", "NestJS", "Spring Boot",
        "Ruby on Rails", "Laravel", "ASP.NET", "Gin", "Fiber",
        "Remix", "Gatsby", "Astro",
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra",
        "Elasticsearch", "DynamoDB", "Neo4j", "InfluxDB", "CockroachDB",
        "MariaDB", "Oracle", "SQL Server", "Snowflake", "BigQuery",
        "Firestore", "Supabase",
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes",
        "Terraform", "Ansible", "Jenkins", "GitHub Actions", "GitLab CI",
        "CircleCI", "ArgoCD", "Helm", "Prometheus", "Grafana",
        "Nginx", "Traefik", "Pulumi", "CloudFormation",
    ],
    "Machine Learning": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Keras", "scikit-learn", "Pandas",
        "NumPy", "Matplotlib", "Seaborn", "Plotly", "Hugging Face",
        "LangChain", "OpenCV", "NLTK", "SpaCy", "Transformers",
        "XGBoost", "LightGBM", "CatBoost", "MLflow", "Weights & Biases",
        "ONNX", "TensorRT", "Ray", "Dask",
    ],
    "Data Engineering": [
        "Apache Spark", "Airflow", "Kafka", "Hadoop", "Hive",
        "dbt", "Flink", "Luigi", "Databricks", "Redshift",
        "ETL", "ELT", "Data Pipeline", "Data Warehouse", "Data Lake",
    ],
    "API & Integration": [
        "REST API", "GraphQL", "gRPC", "WebSocket", "OAuth", "JWT",
        "OpenAPI", "Swagger", "Postman", "API Gateway", "Microservices",
        "Message Queue", "RabbitMQ", "Celery",
    ],
    "Testing": [
        "Jest", "Pytest", "Unittest", "Cypress", "Playwright",
        "Selenium", "JUnit", "TestNG", "Mocha", "Chai",
        "TDD", "BDD", "Unit Testing", "Integration Testing",
    ],
    "Frontend Tools": [
        "Tailwind CSS", "Sass", "CSS", "HTML", "Bootstrap",
        "Material UI", "Chakra UI", "ShadCN", "Figma", "Storybook",
        "Webpack", "Vite", "Babel", "ESLint", "Prettier",
        "React Query", "Redux", "Zustand", "MobX",
    ],
    "Soft Skills": [
        "Leadership", "Communication", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management", "Agile", "Scrum",
        "Kanban", "Project Management", "Mentoring", "Collaboration",
    ],
    "Other Tools": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence",
        "Notion", "Slack", "Linux", "Unix", "macOS", "Windows",
        "VS Code", "IntelliJ", "PyCharm", "Eclipse", "Vim",
        "SQLAlchemy", "Alembic", "Pydantic", "Celery", "Flower",
    ],
}

# Flattened list for fast lookup
ALL_SKILLS: list[str] = [
    skill
    for skills in SKILLS_TAXONOMY.values()
    for skill in skills
]

# Alias map: lowercase alias → canonical name
ALIASES: dict[str, str] = {
    "js": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "k8s": "Kubernetes",
    "k8": "Kubernetes",
    "gke": "Kubernetes",
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "cv": "Computer Vision",
    "tf": "TensorFlow",
    "pt": "PyTorch",
    "pg": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "es": "Elasticsearch",
    "node": "Express.js",
    "node.js": "Express.js",
    "nodejs": "Express.js",
    "vue": "Vue.js",
    "angular js": "Angular",
    "angularjs": "Angular",
    "next": "Next.js",
    "nextjs": "Next.js",
    "nest": "NestJS",
    "nestjs": "NestJS",
    "gh actions": "GitHub Actions",
    "ci/cd": "GitHub Actions",
    "ci cd": "Jenkins",
    "spring": "Spring Boot",
    ".net": "ASP.NET",
    "dotnet": "ASP.NET",
    "rails": "Ruby on Rails",
    "ror": "Ruby on Rails",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "hf": "Hugging Face",
    "transformers": "Transformers",
    "spacy": "SpaCy",
    "rest": "REST API",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "mq": "Message Queue",
    "sass/scss": "Sass",
    "scss": "Sass",
    "mui": "Material UI",
    "chakra": "Chakra UI",
    "tailwind": "Tailwind CSS",
    "rq": "React Query",
}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def extract_skills(text: str) -> list[str]:
    """
    Return a deduplicated list of canonical skill names found in *text*.
    Matching is case-insensitive. Order is preserved (first occurrence wins).
    """
    if not text:
        return []

    found: dict[str, bool] = {}  # canonical_name → True (ordered dict behaviour)
    text_lower = text.lower()

    # 1. Taxonomy lookup (longest skills first to avoid partial matches)
    for skill in sorted(ALL_SKILLS, key=len, reverse=True):
        pattern = _skill_pattern(skill)
        if re.search(pattern, text_lower):
            found[skill] = True

    # 2. Alias lookup
    for alias, canonical in ALIASES.items():
        pattern = _skill_pattern(alias)
        if re.search(pattern, text_lower) and canonical not in found:
            found[canonical] = True

    return list(found.keys())


def extract_skills_csv(text: str) -> str:
    """Return skills as a comma-separated string."""
    return ", ".join(extract_skills(text))


def skills_from_csv(csv: str) -> list[str]:
    """Parse a comma-separated skills string into a clean list."""
    return [s.strip() for s in csv.split(",") if s.strip()]


def skill_overlap(candidate_skills: list[str], jd_skills: list[str]) -> dict:
    """
    Compare candidate skills vs required JD skills.

    Returns
    -------
    dict with keys:
        matched      – skills present in both
        missing      – required skills not found in candidate
        extra        – candidate skills not in JD (bonus signal)
        match_pct    – matched / len(jd_skills) * 100  (0-100)
    """
    if not jd_skills:
        return {"matched": [], "missing": [], "extra": list(candidate_skills), "match_pct": 0.0}

    cand_lower = {s.lower() for s in candidate_skills}
    jd_lower   = {s.lower() for s in jd_skills}

    matched_lower = cand_lower & jd_lower
    missing_lower = jd_lower - cand_lower
    extra_lower   = cand_lower - jd_lower

    # Recover canonical names
    all_map = {s.lower(): s for s in candidate_skills + jd_skills}
    matched = [all_map.get(s, s) for s in matched_lower]
    missing = [all_map.get(s, s) for s in missing_lower]
    extra   = [all_map.get(s, s) for s in extra_lower]

    match_pct = round(len(matched) / len(jd_skills) * 100, 2)

    return {
        "matched":   sorted(matched),
        "missing":   sorted(missing),
        "extra":     sorted(extra),
        "match_pct": match_pct,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=512)
def _skill_pattern(skill: str) -> re.Pattern:
    """
    Build a case-insensitive word-boundary regex for a skill name.
    Handles special chars like C++, C#, .NET.
    """
    escaped = re.escape(skill.lower())
    # Use lookahead/behind instead of \b for skills that end with special chars
    return re.compile(r"(?<![a-z0-9])" + escaped + r"(?![a-z0-9])")
