import re
import os
import joblib
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# STEP 1: LOAD DATA
# ============================================================

print("Loading freelancer data...")


DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "freelancers.csv"
)


freelancers = pd.read_csv(
    DATA_PATH
)


print(
    "Freelancers loaded:",
    len(freelancers)
)



# ============================================================
# STEP 2: LOAD TRAINED XGBOOST MODEL
# ============================================================

print("Loading XGBoost model...")


MODEL_PATH = os.path.join(
    BASE_DIR,
    "xgboost_freelancer_model.pkl"
)


model = joblib.load(
    MODEL_PATH
)


print(
    "XGBoost model loaded!"
)



# ============================================================
# STEP 3: LOAD SENTENCE TRANSFORMER
# ============================================================

print("Loading Sentence Transformer...")


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


print(
    "Embedding model loaded!"
)
# ============================================================
# STEP 4: CLEAN TEXT
# ============================================================

def normalize_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-zA-Z0-9+#.\s-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


text_columns = [
    "title",
    "skills",
    "description",
    "profile_text"
]

for column in text_columns:

    freelancers[column] = (
        freelancers[column]
        .fillna("")
        .astype(str)
    )


# ============================================================
# STEP 5: CREATE FREELANCER PROFILE TEXT
# ============================================================

freelancers["combined_profile"] = (

    freelancers["title"] + " " +

    freelancers["skills"] + " " +

    freelancers["description"] + " " +

    freelancers["profile_text"]
)

freelancers["combined_profile"] = (
    freelancers["combined_profile"]
    .apply(normalize_text)
)


# ============================================================
# STEP 6: CREATE FREELANCER EMBEDDINGS
# ============================================================

print("\nCreating freelancer embeddings...")
freelancer_embeddings = embedding_model.encode(

    freelancers["combined_profile"].tolist(),

    show_progress_bar=True
)
print("Embeddings created!")


# ============================================================
# STEP 7: SKILL ALIASES
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

    "react": [
        "react",
        "react.js",
        "reactjs",
        "react js"
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

    "sql": [
        "sql"
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
        "mongo db"
    ],

    "machine learning": [
        "machine learning",
        "machine-learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "deep-learning"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "nlp": [
        "nlp",
        "natural language processing"
    ],

    "computer vision": [
        "computer vision",
        "opencv"
    ],

    "data science": [
        "data science",
        "data scientist"
    ],

    "data analysis": [
        "data analysis",
        "data analyst"
    ],

    "power bi": [
        "power bi",
        "powerbi"
    ],

    "excel": [
        "excel",
        "microsoft excel"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "azure": [
        "azure",
        "microsoft azure"
    ],

    "docker": [
        "docker"
    ],

    "kubernetes": [
        "kubernetes",
        "k8s"
    ],

    "flutter": [
        "flutter"
    ],

    "android": [
        "android",
        "android development"
    ],

    "ios": [
        "ios",
        "ios development"
    ],

    "php": [
        "php"
    ],

    "laravel": [
        "laravel"
    ],

    "wordpress": [
        "wordpress"
    ],

    "figma": [
        "figma"
    ],

    "photoshop": [
        "photoshop",
        "adobe photoshop"
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

    "ui/ux": [
        "ui ux",
        "ui/ux",
        "ux design",
        "ui design"
    ],

    "blockchain": [
        "blockchain"
    ],

    "solidity": [
        "solidity"
    ]
}

# ============================================================
# STEP 8: EXTRACT SKILLS
# ============================================================

def extract_skills_from_text(text):

    text = normalize_text(text)

    detected = []

    for canonical_skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            alias = normalize_text(alias)

            pattern = (
                r"(?<!\w)"
                + re.escape(alias)
                + r"(?!\w)"
            )

            if re.search(pattern, text):

                detected.append(canonical_skill)

                break

    return sorted(set(detected))


# Detect freelancer skills from complete profile
freelancers["detected_skills"] = (
    freelancers["combined_profile"]
    .apply(extract_skills_from_text)
)


# ============================================================
# STEP 9: NUMERICAL NORMALIZATION
# ============================================================

def normalize_series(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    min_value = series.min()
    max_value = series.max()

    if pd.isna(min_value) or pd.isna(max_value):

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
# STEP 10: PROJECT SKILL EXTRACTION
# ============================================================

def extract_project_skills(project_text):

    return extract_skills_from_text(
        project_text
    )

# ============================================================
# STEP 11: SKILL MATCHING
# ============================================================

def calculate_skill_match(
    required_skills,
    freelancer_skills
):

    required = set(required_skills)

    freelancer = set(freelancer_skills)

    if not required:

        return 0.0, []

    matching = sorted(
        required.intersection(freelancer)
    )

    score = (
        len(matching) / len(required)
    )

    return score, matching


# ============================================================
# STEP 12: BUDGET COMPATIBILITY
# ============================================================

def budget_compatibility(
    freelancer_rate,
    project_low,
    project_high
):

    try:

        freelancer_rate = float(
            freelancer_rate
        )

        project_low = float(
            project_low
        )

        project_high = float(
            project_high
        )

    except:

        return 0.5


    if (
        pd.isna(freelancer_rate)
        or
        pd.isna(project_low)
        or
        pd.isna(project_high)
    ):

        return 0.5


    if (
        project_low
        <= freelancer_rate
        <= project_high
    ):

        return 1.0


    if freelancer_rate < project_low:

        difference = (
            project_low
            -
            freelancer_rate
        )

    else:

        difference = (
            freelancer_rate
            -
            project_high
        )


    range_size = (
        project_high - project_low
    )

    if range_size <= 0:
        return 0.0


    score = (
        1 - difference / range_size
    )

    return max(
        0.0,
        min(1.0, score)
    )


# ============================================================
# STEP 13: MAIN RECOMMENDATION FUNCTION
# ============================================================

def recommend_freelancers(

    project_title,

    project_description,

    project_skills="",

    project_country="",

    project_budget=None,

    hourly_low=None,

    hourly_high=None,

    top_k=5

):

    print("\nSTARTING FREELANCER RECOMMENDATION")

    # --------------------------------------------------------
    # CREATE PROJECT TEXT
    # --------------------------------------------------------

    project_text = (

        str(project_title)
        + " "
        +
        str(project_description)
        + " "
        +
        str(project_skills)
    )


    project_text = normalize_text(
        project_text
    )


    # --------------------------------------------------------
    # EXTRACT REQUIRED SKILLS
    # --------------------------------------------------------

    required_skills = (
        extract_project_skills(
            project_text
        )
    )


    print("\nRequired skills:")

    print(
        required_skills
    )


    # --------------------------------------------------------
    # PROJECT EMBEDDING
    # --------------------------------------------------------

    project_embedding = (
        embedding_model.encode(
            [project_text]
        )
    )


    # --------------------------------------------------------
    # COSINE SIMILARITY
    # --------------------------------------------------------

    similarities = cosine_similarity(

        project_embedding,

        freelancer_embeddings

    )[0]


    # --------------------------------------------------------
    # CREATE FEATURE ROWS
    # --------------------------------------------------------

    prediction_rows = []

    output_rows = []


    for freelancer_index, freelancer in (
        freelancers.iterrows()
    ):


        # ====================================================
        # COSINE SIMILARITY
        # ====================================================

        similarity = float(
            similarities[
                freelancer_index
            ]
        )


        # ====================================================
        # SKILL MATCH
        # ====================================================

        skill_score, matching_skills = (

            calculate_skill_match(

                required_skills,

                freelancer[
                    "detected_skills"
                ]

            )
        )


        # ====================================================
        # BUDGET
        # ====================================================

        budget_score = (

            budget_compatibility(

                freelancer[
                    "hourly_rate"
                ],

                hourly_low,

                hourly_high

            )
        )


        # ====================================================
        # COUNTRY MATCH
        # ====================================================

        freelancer_country = normalize_text(

            freelancer[
                "country"
            ]
        )

        requested_country = normalize_text(
            project_country
        )


        if (

            requested_country
            and
            freelancer_country
            and
            requested_country != "nan"
            and
            freelancer_country != "nan"

        ):

            country_match = int(

                freelancer_country
                ==
                requested_country

            )

        else:

            country_match = 0


        # ====================================================
        # NUMERICAL FEATURES
        # ====================================================

        hourly_rate = pd.to_numeric(

            freelancer[
                "hourly_rate"
            ],

            errors="coerce"

        )


        project_budget_numeric = pd.to_numeric(

            project_budget,
            errors="coerce"

        )


        # ====================================================
        # CREATE MODEL INPUT
        # ====================================================

        row = {

            "cosine_similarity":
                similarity,

            "skill_match":
                skill_score,

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

            "hourly_rate":
                hourly_rate,

            "project_budget":
                project_budget_numeric,

            "hourly_low":
                hourly_low,

            "hourly_high":
                hourly_high,

            "budget_compatibility":
                budget_score,

            "country_match":
                country_match,

            "matching_skill_count":
                len(matching_skills),

            "required_skill_count":
                len(required_skills)

        }


        prediction_rows.append(row)


        # ====================================================
        # STORE OUTPUT INFORMATION
        # ====================================================

        output_rows.append({

            "freelancer_id":
                freelancer[
                    "freelancer_id"
                ],

            "freelancer_name":
                freelancer[
                    "name"
                ],

            "title":
                freelancer[
                    "title"
                ],

            "matching_skills":
                ", ".join(
                    matching_skills
                ),

            "required_skills":
                ", ".join(
                    required_skills
                ),

            "cosine_similarity":
                similarity,

            "skill_match":
                skill_score,

            "experience_score":
                freelancer[
                    "experience_normalized"
                ],

            "job_success":
                freelancer[
                    "job_success_normalized"
                ],

            "hourly_rate":
                hourly_rate,

            "budget_compatibility":
                budget_score,

            "country_match":
                country_match

        })


    # ========================================================
    # CREATE MODEL DATAFRAME
    # ========================================================

    X_new = pd.DataFrame(
        prediction_rows
    )


    # Replace missing numerical values
    X_new = X_new.fillna(0)


    # ========================================================
    # XGBOOST PREDICTION
    # ========================================================

    # Fix numeric columns
    if "hourly_low" in X_new.columns:

        X_new["hourly_low"] = pd.to_numeric(
            X_new["hourly_low"],
            errors="coerce"
        )

    if "hourly_high" in X_new.columns:

        X_new["hourly_high"] = pd.to_numeric(
            X_new["hourly_high"],
            errors="coerce"
        )

    if "hourly_low" in X_new.columns:

        X_new["hourly_low"] = (
            X_new["hourly_low"]
            .fillna(0)
        )

    if "hourly_high" in X_new.columns:

        X_new["hourly_high"] = (
            X_new["hourly_high"]
            .fillna(0)
        )

    print(
        "\nRunning XGBoost predictions..."
    )

    probabilities = model.predict_proba(
        X_new
    )[:, 1]

    predictions = model.predict(
        X_new
    )

    # ========================================================
    # ADD PREDICTIONS
    # ========================================================

    results = pd.DataFrame(
        output_rows
    )


    results[
        "recommendation_probability"
    ] = probabilities


    results[
        "prediction"
    ] = predictions


    # ========================================================
    # RANK FREELANCERS
    # ========================================================

    results = results.sort_values(

        "recommendation_probability",
        ascending=False

    ).reset_index(
        drop=True
    )


    results[
        "rank"
    ] = (
        results.index + 1
    )


    # ========================================================
    # TOP K
    # ========================================================

    top_results = results.head(
        top_k
    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print("\nTOP FREELANCER RECOMMENDATIONS")

    for _, row in top_results.iterrows():

        print(
            f"\nRank {row['rank']}"
        )

        print(
            "Freelancer:",
            row[
                "freelancer_name"
            ]
        )

        print(
            "Title:",
            row[
                "title"
            ]
        )

        print(
            "Recommendation Probability:",
            round(
                row[
                    "recommendation_probability"
                ],
                4
            )
        )

        print(
            "Cosine Similarity:",
            round(
                row[
                    "cosine_similarity"
                ],
                4
            )
        )

        print(
            "Skill Match:",
            round(
                row[
                    "skill_match"
                ],
                4
            )
        )

        print(
            "Matching Skills:",
            row[
                "matching_skills"
            ]
        )

        print(
            "Required Skills:",
            row[
                "required_skills"
            ]
        )

        print(
            "Experience Score:",
            round(
                row[
                    "experience_score"
                ],
                4
            )
        )

        print(
            "Job Success:",
            round(
                row[
                    "job_success"
                ],
                4
            )
        )

        print(
            "Hourly Rate:",
            row[
                "hourly_rate"
            ]
        )

        print(
            "Budget Compatibility:",
            round(
                row[
                    "budget_compatibility"
                ],
                4
            )
        )


    # ========================================================
    # SAVE RESULTS
    # ========================================================

    RESULT_PATH = os.path.join(
        BASE_DIR,
        "data",
        "recommendation_results.csv"
    )

    results.to_csv(
        RESULT_PATH,
        index=False
    )

    print(
        "\nFull results saved to:"
        " data/recommendation_results.csv"
    )

    return top_results

# ============================================================
# STEP 14: DYNAMIC USER / AGENT INPUT
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("FREELANCER RECOMMENDATION SYSTEM")
    print("=" * 60)

    print("\nEnter the project requirement.")
    print("You can provide the JSON generated by:")
    print("1. Requirement Understanding Agent")
    print("2. Complexity Prediction Agent")
    print()

    # --------------------------------------------------------
    # IMPORT JSON
    # --------------------------------------------------------

    import json

    json_input = input(
        "Paste the complete project JSON here:\n"
    )

    try:

        project_data = json.loads(
            json_input
        )

    except json.JSONDecodeError:

        print(
            "\nERROR: Invalid JSON input."
        )

        print(
            "Please provide valid JSON."
        )

        exit()


    # ========================================================
    # EXTRACT REQUIREMENT ANALYSIS
    # ========================================================

    requirement_analysis = (
        project_data.get(
            "requirement_analysis",
            {}
        )
    )

    # ========================================================
    # EXTRACT COMPLEXITY ANALYSIS
    # ========================================================

    complexity_analysis = (
        project_data.get(
            "complexity_analysis",
            {}
        )
    )


    # ========================================================
    # PROJECT DOMAIN
    # ========================================================

    project_domain = (
        requirement_analysis.get(
            "project_domain",
            ""
        )
    )


    # ========================================================
    # PROJECT TYPE
    # ========================================================

    project_type = (
        requirement_analysis.get(
            "project_type",
            ""
        )
    )


    # ========================================================
    # TARGET USERS
    # ========================================================

    target_users = (
        requirement_analysis.get(
            "target_users",
            []
        )
    )

    if not isinstance(
        target_users,
        list
    ):

        target_users = [
            str(target_users)
        ]


    # ========================================================
    # FEATURES
    # ========================================================

    features = (
        requirement_analysis.get(
            "features",
            []
        )
    )

    if not isinstance(
        features,
        list
    ):

        features = [
            str(features)
        ]


    # ========================================================
    # TECHNOLOGY PREFERENCE
    # ========================================================

    technology_preference = (
        requirement_analysis.get(
            "technology_preference",
            ""
        )
    )

    if technology_preference is None:
        technology_preference = ""


    # ========================================================
    # PLATFORM
    # ========================================================

    platform = (
        requirement_analysis.get(
            "platform",
            ""
        )
    )


    # ========================================================
    # DEADLINE
    # ========================================================

    deadline = (
        requirement_analysis.get(
            "deadline",
            ""
        )
    )


    # ========================================================
    # BUDGET RANGE
    # ========================================================

    budget_range = (
        requirement_analysis.get(
            "budget_range",
            ""
        )
    )


    # ========================================================
    # ADDITIONAL REQUIREMENTS
    # ========================================================

    additional_requirements = (
        requirement_analysis.get(
            "additional_requirements",
            []
        )
    )

    if not isinstance(
        additional_requirements,
        list
    ):

        additional_requirements = [
            str(additional_requirements)
        ]


    # ========================================================
    # COMPLEXITY INFORMATION
    # ========================================================

    complexity_level = (
        complexity_analysis.get(
            "complexity_level",
            ""
        )
    )


    estimated_duration = (
        complexity_analysis.get(
            "estimated_duration",
            ""
        )
    )


    risk_level = (
        complexity_analysis.get(
            "risk_level",
            ""
        )
    )


    reason = (
        complexity_analysis.get(
            "reason",
            ""
        )
    )


    technical_factors = (
        complexity_analysis.get(
            "technical_factors",
            []
        )
    )

    if not isinstance(
        technical_factors,
        list
    ):

        technical_factors = [
            str(technical_factors)
        ]


    # ========================================================
    # CREATE PROJECT TITLE
    # ========================================================

    project_title = (
        str(project_domain)
        + " "
        +
        str(project_type)
    )


    # ========================================================
    # CREATE PROJECT DESCRIPTION
    # ========================================================

    project_description = f"""
    Project Domain:
    {project_domain}

    Project Type:
    {project_type}

    Target Users:
    {", ".join(target_users)}

    Platform:
    {platform}

    Deadline:
    {deadline}

    Budget Range:
    {budget_range}

    Complexity Level:
    {complexity_level}

    Estimated Duration:
    {estimated_duration}

    Risk Level:
    {risk_level}

    Complexity Reason:
    {reason}

    Features:
    {", ".join(features)}

    Additional Requirements:
    {", ".join(additional_requirements)}

    Technical Factors:
    {", ".join(technical_factors)}

    Technology Preference:
    {technology_preference}
    """


    # ========================================================
    # CREATE PROJECT SKILLS TEXT
    # ========================================================

    project_skills = f"""
    {technology_preference}

    {project_type}

    {platform}

    {", ".join(features)}

    {", ".join(technical_factors)}

    {", ".join(additional_requirements)}
    """


    # ========================================================
    # EXTRACT BUDGET VALUES
    # ========================================================

    def extract_budget_values(
        budget_text
    ):

        if not budget_text:

            return None, None, None


        budget_text = str(
            budget_text
        )


        # Remove commas

        budget_text = (
            budget_text
            .replace(",", "")
        )

        values = re.findall(
            r"\d+(?:\.\d+)?",
            budget_text
        )


        values = [

            float(value)

            for value in values

        ]


        if len(values) >= 2:

            low = min(values)

            high = max(values)

            budget = (
                low + high
            ) / 2

            return (
                budget,
                low,
                high
            )


        elif len(values) == 1:

            budget = values[0]

            return (
                budget,
                budget,
                budget
            )


        return (
            None,
            None,
            None
        )


    project_budget, budget_low, budget_high = (
        extract_budget_values(
            budget_range
        )
    )


    # ========================================================
    # IMPORTANT:
    # YOUR DATASET USES HOURLY RATE RANGES.
    #
    # If the project budget is a total project budget such as
    # "$100,000 - $150,000", it should NOT directly be treated
    # as an hourly rate.
    #
    # Therefore, use the extracted values only when they
    # represent a realistic hourly range.
    # ========================================================

    hourly_low = None

    hourly_high = None


    # --------------------------------------------------------
    # CHECK WHETHER BUDGET LOOKS LIKE AN HOURLY RANGE
    # --------------------------------------------------------

    budget_lower_text = (
        str(budget_range)
        .lower()
    )


    if (
        "hour" in budget_lower_text
        or
        "/hr" in budget_lower_text
        or
        "per hour" in budget_lower_text
    ):

        hourly_low = budget_low

        hourly_high = budget_high


    # ========================================================
    # COUNTRY
    # ========================================================

    project_country = (
        requirement_analysis.get(
            "country",
            ""
        )
    )


    # ========================================================
    # DISPLAY PARSED INPUT
    # ========================================================

    print("\n" + "=" * 60)
    print("PROJECT INFORMATION RECEIVED")
    print("=" * 60)

    print(
        "\nProject Title:",
        project_title
    )

    print(
        "Domain:",
        project_domain
    )

    print(
        "Project Type:",
        project_type
    )

    print(
        "Platform:",
        platform
    )

    print(
        "Required Features:"
    )

    for feature in features:

        print(
            " -",
            feature
        )


    print(
        "\nComplexity:",
        complexity_level
    )

    print(
        "Risk:",
        risk_level
    )

    print(
        "Budget:",
        budget_range
    )

    print(
        "Deadline:",
        deadline
    )


    # ========================================================
    # RUN RECOMMENDATION
    # ========================================================

    recommend_freelancers(

        project_title=
        project_title,

        project_description=
        project_description,

        project_skills=
        project_skills,

        project_country=
        project_country,

        project_budget=
        project_budget,

        hourly_low=
        hourly_low,

        hourly_high=
        hourly_high,

        top_k=5

    )