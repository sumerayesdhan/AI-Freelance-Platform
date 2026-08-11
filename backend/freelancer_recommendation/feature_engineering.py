import re
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# STEP 1: LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

freelancers = pd.read_csv("data/freelancers.csv")
projects = pd.read_csv("data/projects.csv")

print("Freelancers:", freelancers.shape)
print("Projects:", projects.shape)


# ============================================================
# STEP 2: CHECK REQUIRED COLUMNS
# ============================================================

freelancer_required_columns = [
    "freelancer_id",
    "name",
    "title",
    "skills",
    "description",
    "profile_text",
    "country",
    "experienceScore",
    "hourly_rate",
    "job_success",
    "total_hours",
    "total_jobs"
]

project_required_columns = [
    "project_id",
    "title",
    "description",
    "project_text",
    "country",
    "budget",
    "hourly_low",
    "hourly_high",
    "is_hourly"
]

for column in freelancer_required_columns:
    if column not in freelancers.columns:
        raise ValueError(
            f"Missing freelancer column: {column}"
        )

for column in project_required_columns:
    if column not in projects.columns:
        raise ValueError(
            f"Missing project column: {column}"
        )

print("\nRequired columns verified.")


# ============================================================
# STEP 3: CLEAN TEXT COLUMNS
# ============================================================

freelancer_text_columns = [
    "title",
    "skills",
    "description",
    "profile_text"
]

project_text_columns = [
    "title",
    "description",
    "project_text"
]


for column in freelancer_text_columns:

    freelancers[column] = (
        freelancers[column]
        .fillna("")
        .astype(str)
    )


for column in project_text_columns:

    projects[column] = (
        projects[column]
        .fillna("")
        .astype(str)
    )


# ============================================================
# STEP 4: NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Convert common separators to spaces
    text = re.sub(
        r"[/|;:_\n\r\t]+",
        " ",
        text
    )

    # Keep letters, numbers, +, #, ., -
    text = re.sub(
        r"[^a-zA-Z0-9+#.\s-]",
        " ",
        text
    )

    # Normalize multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# STEP 5: CREATE COMBINED TEXT
# ============================================================

freelancers["combined_profile"] = (
    freelancers["title"] + " " +
    freelancers["skills"] + " " +
    freelancers["description"] + " " +
    freelancers["profile_text"]
)

projects["combined_project"] = (
    projects["title"] + " " +
    projects["project_text"] + " " +
    projects["description"]
)


freelancers["combined_profile"] = (
    freelancers["combined_profile"]
    .apply(normalize_text)
)

projects["combined_project"] = (
    projects["combined_project"]
    .apply(normalize_text)
)


# ============================================================
# STEP 6: SKILL ALIASES
# ============================================================

SKILL_ALIASES = {

    "python": [
        "python",
        "python3",
        "python developer",
        "python programming"
    ],

    "java": [
        "java",
        "java developer",
        "java programming"
    ],

    "javascript": [
        "javascript",
        "javascript developer",
        "js"
    ],

    "typescript": [
        "typescript",
        "typescript developer"
    ],

    "react": [
        "react",
        "react.js",
        "reactjs",
        "react js"
    ],

    "next.js": [
        "next.js",
        "nextjs",
        "next js"
    ],

    "node.js": [
        "node.js",
        "nodejs",
        "node js"
    ],

    "django": [
        "django"
    ],

    "flask": [
        "flask"
    ],

    "fastapi": [
        "fastapi",
        "fast api"
    ],

    "php": [
        "php"
    ],

    "laravel": [
        "laravel"
    ],

    "ruby": [
        "ruby"
    ],

    "ruby on rails": [
        "ruby on rails",
        "rails"
    ],

    "c++": [
        "c++",
        "cpp"
    ],

    "c#": [
        "c#",
        "c sharp"
    ],

    "sql": [
        "sql",
        "sql programming",
        "sql server",
        "microsoft sql server"
    ],

    "mysql": [
        "mysql"
    ],

    "postgresql": [
        "postgresql",
        "postgres"
    ],

    "mongodb": [
        "mongodb",
        "mongo db",
        "mongo"
    ],

    "firebase": [
        "firebase"
    ],

    "redis": [
        "redis"
    ],

    "machine learning": [
        "machine learning",
        "machine-learning"
    ],

    "deep learning": [
        "deep learning",
        "deep-learning"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "artificial-intelligence"
    ],

    "generative ai": [
        "generative ai",
        "generative artificial intelligence"
    ],

    "natural language processing": [
        "natural language processing",
        "nlp"
    ],

    "computer vision": [
        "computer vision"
    ],

    "data science": [
        "data science",
        "data scientist"
    ],

    "data analysis": [
        "data analysis",
        "data analyst",
        "data analytics"
    ],

    "data engineering": [
        "data engineering",
        "data engineer"
    ],

    "data visualization": [
        "data visualization",
        "data visualisation"
    ],

    "data mining": [
        "data mining"
    ],

    "power bi": [
        "power bi",
        "powerbi"
    ],

    "tableau": [
        "tableau"
    ],

    "looker studio": [
        "looker studio",
        "google looker studio"
    ],

    "excel": [
        "excel",
        "microsoft excel"
    ],

    "google sheets": [
        "google sheets"
    ],

    "pandas": [
        "pandas"
    ],

    "numpy": [
        "numpy"
    ],

    "matplotlib": [
        "matplotlib"
    ],

    "tensorflow": [
        "tensorflow"
    ],

    "pytorch": [
        "pytorch"
    ],

    "scikit-learn": [
        "scikit-learn",
        "scikit learn"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "azure": [
        "azure",
        "microsoft azure"
    ],

    "google cloud": [
        "google cloud",
        "google cloud platform",
        "gcp"
    ],

    "docker": [
        "docker"
    ],

    "kubernetes": [
        "kubernetes",
        "k8s"
    ],

    "apache spark": [
        "apache spark",
        "spark"
    ],

    "apache kafka": [
        "apache kafka",
        "kafka"
    ],

    "airflow": [
        "airflow",
        "apache airflow"
    ],

    "etl": [
        "etl"
    ],

    "wordpress": [
        "wordpress"
    ],

    "shopify": [
        "shopify"
    ],

    "html": [
        "html",
        "html5"
    ],

    "css": [
        "css",
        "css3"
    ],

    "figma": [
        "figma"
    ],

    "photoshop": [
        "photoshop",
        "adobe photoshop"
    ],

    "adobe illustrator": [
        "adobe illustrator",
        "illustrator"
    ],

    "after effects": [
        "after effects",
        "adobe after effects"
    ],

    "video editing": [
        "video editing",
        "video editor"
    ],

    "graphic design": [
        "graphic design",
        "graphic designer"
    ],

    "ui design": [
        "ui design",
        "user interface design"
    ],

    "ux design": [
        "ux design",
        "user experience design"
    ],

    "ui/ux": [
        "ui ux",
        "ui/ux",
        "ux ui"
    ],

    "web development": [
        "web development",
        "web developer"
    ],

    "web scraping": [
        "web scraping",
        "web scraper",
        "web scraping expert"
    ],

    "data extraction": [
        "data extraction"
    ],

    "seo": [
        "seo",
        "search engine optimization"
    ],

    "digital marketing": [
        "digital marketing"
    ],

    "affiliate marketing": [
        "affiliate marketing"
    ],

    "content writing": [
        "content writing",
        "content writer"
    ],

    "article writing": [
        "article writing"
    ],

    "academic writing": [
        "academic writing",
        "academic writer"
    ],

    "medical writing": [
        "medical writing",
        "medical writer"
    ],

    "blockchain": [
        "blockchain"
    ],

    "solidity": [
        "solidity"
    ],

    "ethereum": [
        "ethereum"
    ],

    "web3": [
        "web3",
        "web 3"
    ],

    "chatgpt": [
        "chatgpt"
    ],

    "openai": [
        "openai",
        "open ai"
    ],

    "llm": [
        "llm",
        "large language model",
        "large language models"
    ],

    "prompt engineering": [
        "prompt engineering",
        "prompt engineer"
    ],

    "lead generation": [
        "lead generation"
    ],

    "customer service": [
        "customer service",
        "customer support"
    ],

    "recruitment": [
        "recruitment",
        "recruiting",
        "talent acquisition"
    ],

    "portuguese": [
        "portuguese"
    ],

    "french": [
        "french"
    ],

    "german": [
        "german"
    ],

    "english": [
        "english"
    ]
}


# ============================================================
# STEP 7: BUILD SKILL EXTRACTION FUNCTION
# ============================================================

def extract_skills_from_text(text):

    text = normalize_text(text)

    detected_skills = set()

    if not text:
        return []

    for canonical_skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            alias = normalize_text(alias)

            if not alias:
                continue

            # Exact word/phrase boundary
            pattern = (
                r"(?<![a-zA-Z0-9])"
                + re.escape(alias)
                + r"(?![a-zA-Z0-9])"
            )

            if re.search(pattern, text):

                detected_skills.add(
                    canonical_skill
                )

                break

    return sorted(detected_skills)


# ============================================================
# STEP 8: EXTRACT FREELANCER SKILLS
# ============================================================

print("\nExtracting freelancer skills...")

freelancers["skill_source_text"] = (
    freelancers["title"] + " " +
    freelancers["skills"] + " " +
    freelancers["description"] + " " +
    freelancers["profile_text"]
)


freelancers["detected_skills"] = (
    freelancers["skill_source_text"]
    .apply(extract_skills_from_text)
)


print("\nSample freelancer skill extraction:")

for i in range(min(10, len(freelancers))):

    print(
        "\n",
        freelancers.loc[i, "name"]
    )

    print(
        "Skills:",
        freelancers.loc[i, "detected_skills"]
    )


# ============================================================
# STEP 9: EXTRACT PROJECT REQUIRED SKILLS
# ============================================================

print("\nExtracting project required skills...")


projects["required_skills"] = (
    projects["combined_project"]
    .apply(extract_skills_from_text)
)


print("\nSample project skill extraction:")

for i in range(min(10, len(projects))):

    print(
        "\nProject:",
        projects.loc[i, "title"]
    )

    print(
        "Required skills:",
        projects.loc[i, "required_skills"]
    )


# ============================================================
# STEP 10: CALCULATE SKILL MATCH
# ============================================================

def calculate_skill_match(
    required_skills,
    freelancer_skills
):

    required = set(required_skills)

    freelancer = set(freelancer_skills)

    # No identifiable project skills
    if len(required) == 0:

        return 0.0, []

    matching = sorted(
        required.intersection(freelancer)
    )

    score = (
        len(matching) /
        len(required)
    )

    return score, matching


# ============================================================
# STEP 11: NUMERICAL NORMALIZATION
# ============================================================

def normalize_series(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    min_value = series.min()
    max_value = series.max()

    if (
        pd.isna(min_value)
        or
        pd.isna(max_value)
    ):

        return pd.Series(
            0.5,
            index=series.index
        )

    if max_value == min_value:

        return pd.Series(
            1.0,
            index=series.index
        )

    return (
        (series - min_value)
        /
        (max_value - min_value)
    )


# ============================================================
# STEP 12: NORMALIZE FREELANCER FEATURES
# ============================================================

print("\nNormalizing numerical features...")


freelancers["experience_normalized"] = (
    normalize_series(
        freelancers["experienceScore"]
    )
)


freelancers["job_success_normalized"] = (
    normalize_series(
        freelancers["job_success"]
    )
)


freelancers["total_jobs_normalized"] = (
    normalize_series(
        freelancers["total_jobs"]
    )
)


freelancers["total_hours_normalized"] = (
    normalize_series(
        freelancers["total_hours"]
    )
)


# ============================================================
# STEP 13: BUDGET COMPATIBILITY
# ============================================================

def budget_compatibility(
    freelancer_rate,
    project_low,
    project_high
):

    freelancer_rate = pd.to_numeric(
        freelancer_rate,
        errors="coerce"
    )

    project_low = pd.to_numeric(
        project_low,
        errors="coerce"
    )

    project_high = pd.to_numeric(
        project_high,
        errors="coerce"
    )

    if (
        pd.isna(freelancer_rate)
        or
        pd.isna(project_low)
        or
        pd.isna(project_high)
    ):

        return 0.5

    # Make sure range is valid
    if project_low > project_high:

        project_low, project_high = (
            project_high,
            project_low
        )

    # Freelancer rate is within range
    if (
        project_low
        <= freelancer_rate
        <= project_high
    ):

        return 1.0

    # Calculate distance
    if freelancer_rate < project_low:

        difference = (
            project_low -
            freelancer_rate
        )

    else:

        difference = (
            freelancer_rate -
            project_high
        )

    range_size = (
        project_high -
        project_low
    )

    # If range has no width
    if range_size == 0:

        return 0.0

    score = (
        1 -
        difference /
        range_size
    )

    return max(
        0.0,
        min(1.0, score)
    )


# ============================================================
# STEP 14: LOAD SENTENCE TRANSFORMER
# ============================================================

print("\n" + "=" * 70)
print("LOADING SENTENCE TRANSFORMER")
print("=" * 70)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# STEP 15: CREATE FREELANCER EMBEDDINGS
# ============================================================

print("\nCreating freelancer embeddings...")


freelancer_embeddings = model.encode(
    freelancers["combined_profile"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)


print(
    "Freelancer embedding shape:",
    freelancer_embeddings.shape
)


# ============================================================
# STEP 16: CREATE PROJECT EMBEDDINGS
# ============================================================

print("\nCreating project embeddings...")


project_embeddings = model.encode(
    projects["combined_project"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)


print(
    "Project embedding shape:",
    project_embeddings.shape
)


# ============================================================
# STEP 17: CREATE PROJECT × FREELANCER FEATURES
# ============================================================

print("\n" + "=" * 70)
print("CREATING PROJECT × FREELANCER FEATURES")
print("=" * 70)


feature_rows = []


for project_index, project in projects.iterrows():

    print(
        f"Processing project "
        f"{project_index + 1}/{len(projects)}"
    )

    # --------------------------------------------------------
    # PROJECT EMBEDDING
    # --------------------------------------------------------

    project_vector = (
        project_embeddings[
            project_index
        ]
        .reshape(1, -1)
    )


    # --------------------------------------------------------
    # COSINE SIMILARITY
    # --------------------------------------------------------

    similarities = cosine_similarity(
        project_vector,
        freelancer_embeddings
    )[0]


    # --------------------------------------------------------
    # PROJECT REQUIRED SKILLS
    # --------------------------------------------------------

    required_skills = (
        project["required_skills"]
    )


    # --------------------------------------------------------
    # LOOP THROUGH FREELANCERS
    # --------------------------------------------------------

    for freelancer_index, freelancer in (
        freelancers.iterrows()
    ):

        # ----------------------------------------------------
        # COSINE SIMILARITY
        # ----------------------------------------------------

        similarity = float(
            similarities[
                freelancer_index
            ]
        )


        # ----------------------------------------------------
        # SKILL MATCH
        # ----------------------------------------------------

        skill_score, matching_skills = (
            calculate_skill_match(
                required_skills,
                freelancer[
                    "detected_skills"
                ]
            )
        )


        # ----------------------------------------------------
        # BUDGET COMPATIBILITY
        # ----------------------------------------------------

        budget_score = (
            budget_compatibility(
                freelancer[
                    "hourly_rate"
                ],

                project[
                    "hourly_low"
                ],

                project[
                    "hourly_high"
                ]
            )
        )


        # ----------------------------------------------------
        # COUNTRY MATCH
        # ----------------------------------------------------

        freelancer_country = (
            normalize_text(
                freelancer["country"]
            )
        )

        project_country = (
            normalize_text(
                project["country"]
            )
        )


        if (
            freelancer_country
            and
            project_country
            and
            freelancer_country != "nan"
            and
            project_country != "nan"
        ):

            country_match = int(
                freelancer_country
                ==
                project_country
            )

        else:

            country_match = 0


        # ----------------------------------------------------
        # CREATE FEATURE ROW
        # ----------------------------------------------------

        row = {

            # IDs
            "project_id":
                project["project_id"],

            "freelancer_id":
                freelancer["freelancer_id"],


            # Basic information
            "project_title":
                project["title"],

            "freelancer_name":
                freelancer["name"],


            # ------------------------------------------------
            # MAIN ML FEATURES
            # ------------------------------------------------

            "cosine_similarity":
                similarity,

            "skill_match":
                float(skill_score),

            "matching_skills":
                ", ".join(
                    matching_skills
                ),

            "required_skills":
                ", ".join(
                    required_skills
                ),


            # ------------------------------------------------
            # FREELANCER PERFORMANCE
            # ------------------------------------------------

            "experience_score":
                freelancer[
                    "experience_normalized"
                ],

            "job_success":
                freelancer[
                    "job_success_normalized"
                ],

            "total_jobs":
                freelancer[
                    "total_jobs_normalized"
                ],

            "total_hours":
                freelancer[
                    "total_hours_normalized"
                ],


            # ------------------------------------------------
            # PRICING
            # ------------------------------------------------

            "hourly_rate":
                pd.to_numeric(
                    freelancer[
                        "hourly_rate"
                    ],
                    errors="coerce"
                ),

            "project_budget":
                pd.to_numeric(
                    project[
                        "budget"
                    ],
                    errors="coerce"
                ),

            "hourly_low":
                pd.to_numeric(
                    project[
                        "hourly_low"
                    ],
                    errors="coerce"
                ),

            "hourly_high":
                pd.to_numeric(
                    project[
                        "hourly_high"
                    ],
                    errors="coerce"
                ),

            "budget_compatibility":
                float(budget_score),


            # ------------------------------------------------
            # LOCATION
            # ------------------------------------------------

            "country_match":
                country_match
        }


        feature_rows.append(row)


# ============================================================
# STEP 18: CREATE DATAFRAME
# ============================================================

print("\nCreating feature dataframe...")


features = pd.DataFrame(
    feature_rows
)


# ============================================================
# STEP 19: CLEAN NUMERICAL FEATURES
# ============================================================

numeric_columns = [

    "cosine_similarity",

    "skill_match",

    "experience_score",

    "job_success",

    "total_jobs",

    "total_hours",

    "hourly_rate",

    "project_budget",

    "hourly_low",

    "hourly_high",

    "budget_compatibility",

    "country_match"
]


for column in numeric_columns:

    features[column] = pd.to_numeric(
        features[column],
        errors="coerce"
    )


features[numeric_columns] = (
    features[numeric_columns]
    .fillna(0)
)


# ============================================================
# STEP 20: ROUND NUMERICAL VALUES
# ============================================================

features["cosine_similarity"] = (
    features["cosine_similarity"]
    .round(4)
)

features["skill_match"] = (
    features["skill_match"]
    .round(4)
)

features["experience_score"] = (
    features["experience_score"]
    .round(4)
)

features["job_success"] = (
    features["job_success"]
    .round(4)
)

features["budget_compatibility"] = (
    features["budget_compatibility"]
    .round(4)
)


# ============================================================
# STEP 21: CREATE MATCHING SKILL COUNT
# ============================================================

def count_matching_skills(text):

    if not text or pd.isna(text):

        return 0

    return len(
        [
            skill
            for skill in str(text).split(",")
            if skill.strip()
        ]
    )


features["matching_skill_count"] = (
    features["matching_skills"]
    .apply(count_matching_skills)
)


# ============================================================
# STEP 22: CREATE REQUIRED SKILL COUNT
# ============================================================

features["required_skill_count"] = (
    features["required_skills"]
    .apply(count_matching_skills)
)


# ============================================================
# STEP 23: SAVE DATASET
# ============================================================

output_file = (
    "data/recommendation_features.csv"
)


features.to_csv(
    output_file,
    index=False
)


# ============================================================
# STEP 24: DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("FEATURE ENGINEERING COMPLETED")
print("=" * 70)


print(
    "\nFeature dataset shape:",
    features.shape
)


print(
    "\nFeature columns:"
)


for column in features.columns:

    print(
        " -",
        column
    )


# ============================================================
# STEP 25: CHECK SKILL EXTRACTION
# ============================================================

print("\n" + "=" * 70)
print("SKILL EXTRACTION CHECK")
print("=" * 70)


print(
    "\nPROJECT REQUIRED SKILLS:"
)


for i in range(
    min(10, len(projects))
):

    print(
        f"\nProject {projects.loc[i, 'project_id']}:"
    )

    print(
        projects.loc[
            i,
            "required_skills"
        ]
    )


print(
    "\n" + "-" * 70
)


print(
    "\nSAMPLE MATCHING RESULTS:"
)


sample_columns = [
    "project_id",
    "freelancer_id",
    "project_title",
    "freelancer_name",
    "cosine_similarity",
    "skill_match",
    "matching_skills",
    "required_skills"
]


print(
    features[
        sample_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# STEP 26: CHECK SKILL MATCH DISTRIBUTION
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "SKILL MATCH DISTRIBUTION"
)

print(
    "=" * 70
)


print(
    features[
        "skill_match"
    ]
    .describe()
)


print(
    "\nNumber of rows with at least "
    "one matching skill:",
    (
        features[
            "matching_skill_count"
        ] > 0
    ).sum()
)


print(
    "\nNumber of rows with no matching skills:",
    (
        features[
            "matching_skill_count"
        ] == 0
    ).sum()
)


print(
    "\nSaved successfully to:"
)

print(
    output_file
)

print(
    "\nNext step:"
)

print(
    "Train XGBoost using "
    "recommendation_features.csv"
)