"""Shared helpers for report content: paths, data loading, IEEE citations, figure sizing."""

import json
import re
from pathlib import Path

from docx.shared import Inches
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "report" / "figures"
GEN = FIG / "generated"
ORIG = FIG / "original"
SCREENS = FIG / "screens"
EQ = FIG / "equations"
ML_FIG = ROOT / "reports" / "figures"

METRICS = json.loads((ROOT / "reports" / "metrics.json").read_text())["models"]
META = json.loads((ROOT / "backend" / "app" / "artifacts" / "model_meta.json").read_text())
LATENCY = json.loads((ROOT / "report" / "latency.json").read_text())
SYSTEM_TESTS = json.loads((ROOT / "report" / "system_test_results.json").read_text())

TEAM = [("Anup Karki", "380181"), ("Dipesh Kumar Sharma", "380184"), ("Puskar Sarki", "380191")]
SUPERVISOR = "Mr. Sunny Sharma"
COLLEGE = "Aryan School of Engineering and Management"
ADDRESS = "Devkota Sadak, Mid Baneshwor, Kathmandu"
UNIVERSITY = "Purbanchal University"
SUBMIT_DATE = "June, 2026"

# --------------------------------------------------------------------------- references
# All entries verified against Crossref / arXiv / DataCite / publisher pages (IEEE style).
REFERENCES = {
    "savarese": 'G. Savarese, P. M. Becher, L. H. Lund, P. Seferovic, G. M. C. Rosano, and A. J. S. Coats, "Global burden of heart failure: a comprehensive and updated review of epidemiology," *Cardiovascular Research*, vol. 118, no. 17, pp. 3272–3287, 2022, doi: 10.1093/cvr/cvac013.',
    "ahmad": 'T. Ahmad, A. Munir, S. H. Bhatti, M. Aftab, and M. A. Raza, "Survival analysis of heart failure patients: A case study," *PLOS ONE*, vol. 12, no. 7, Art. no. e0181001, Jul. 2017, doi: 10.1371/journal.pone.0181001.',
    "chicco": 'D. Chicco and G. Jurman, "Machine learning can predict survival of patients with heart failure from serum creatinine and ejection fraction alone," *BMC Medical Informatics and Decision Making*, vol. 20, no. 1, Art. no. 16, Feb. 2020, doi: 10.1186/s12911-020-1023-5.',
    "uci": '"Heart Failure Clinical Records," UCI Machine Learning Repository, 2020. [Online]. Available: https://archive.ics.uci.edu/dataset/519, doi: 10.24432/C5Z89R.',
    "detrano": 'R. Detrano, A. Janosi, W. Steinbrunn, M. Pfisterer, J.-J. Schmid, S. Sandhu, K. H. Guppy, S. Lee, and V. Froelicher, "International application of a new probability algorithm for the diagnosis of coronary artery disease," *The American Journal of Cardiology*, vol. 64, no. 5, pp. 304–310, Aug. 1989, doi: 10.1016/0002-9149(89)90524-9.',
    "gudadhe": 'M. Gudadhe, K. Wankhade, and S. Dongre, "Decision support system for heart disease based on support vector machine and artificial neural network," in *Proc. Int. Conf. Computer and Communication Technology (ICCCT)*, Allahabad, India, Sep. 2010, pp. 741–745, doi: 10.1109/ICCCT.2010.5640377.',
    "jabbar": 'M. A. Jabbar, B. L. Deekshatulu, and P. Chandra, "Heart disease prediction system using associative classification and genetic algorithm," in *Proc. Int. Conf. Emerging Trends in Electrical, Electronics and Communication Technologies (ICECIT)*, vol. 1, Elsevier, Dec. 2012, pp. 183–192. [Online]. Available: arXiv:1303.5919.',
    "mohan": 'S. Mohan, C. Thirumalai, and G. Srivastava, "Effective heart disease prediction using hybrid machine learning techniques," *IEEE Access*, vol. 7, pp. 81542–81554, 2019, doi: 10.1109/ACCESS.2019.2923707.',
    "lakshman": 'S. K. Lakshmanaprabu, S. N. Mohanty, K. Shankar, N. Arunkumar, and G. Ramirez, "Optimal deep learning model for classification of lung cancer on CT images," *Future Generation Computer Systems*, vol. 92, pp. 374–382, Mar. 2019, doi: 10.1016/j.future.2018.10.009.',
    "alaa": 'A. M. Alaa and M. van der Schaar, "Forecasting individualized disease trajectories using interpretable deep learning," arXiv preprint arXiv:1810.10489, Oct. 2018.',
    "breiman": 'L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, Oct. 2001, doi: 10.1023/A:1010933404324.',
    "quinlan": 'J. R. Quinlan, "Induction of decision trees," *Machine Learning*, vol. 1, no. 1, pp. 81–106, Mar. 1986, doi: 10.1007/BF00116251.',
    "friedman": 'J. H. Friedman, "Greedy function approximation: A gradient boosting machine," *The Annals of Statistics*, vol. 29, no. 5, pp. 1189–1232, Oct. 2001, doi: 10.1214/aos/1013203451.',
    "chen": 'T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD \'16)*, San Francisco, CA, USA, Aug. 2016, pp. 785–794, doi: 10.1145/2939672.2939785.',
    "lundberg2017": 'S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Advances in Neural Information Processing Systems 30 (NIPS 2017)*, Long Beach, CA, USA, 2017, pp. 4765–4774.',
    "lundberg2020": 'S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, B. Nair, R. Katz, J. Himmelfarb, N. Bansal, and S.-I. Lee, "From local explanations to global understanding with explainable AI for trees," *Nature Machine Intelligence*, vol. 2, no. 1, pp. 56–67, Jan. 2020, doi: 10.1038/s42256-019-0138-9.',
    "pedregosa": 'F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, M. Brucher, M. Perrot, and E. Duchesnay, "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.',
}

BIBLIOGRAPHY = [
    'FastAPI Documentation. [Online]. Available: https://fastapi.tiangolo.com',
    'React Documentation. [Online]. Available: https://react.dev',
    'XGBoost Documentation. [Online]. Available: https://xgboost.readthedocs.io',
    'Scikit-learn User Guide. [Online]. Available: https://scikit-learn.org/stable/user_guide.html',
    'PlantUML Language Reference Guide. [Online]. Available: https://plantuml.com',
    'jsPDF Documentation. [Online]. Available: https://github.com/parallax/jsPDF',
]


class Citations:
    """Assigns IEEE numbers in order of first citation. Use [@key] or [@a,b] in text."""

    def __init__(self, labels=None):
        self.order: list[str] = []
        self.labels = labels or {}  # cross-reference numbers from the previous build pass

    def __call__(self, text: str) -> str:
        text = re.sub(r"\{((?:fig|tab):[a-z0-9_]+)\}", lambda m: str(self.labels.get(m.group(1), "?")), text)
        def repl(m):
            nums = []
            for key in m.group(1).split(","):
                key = key.strip()
                if key not in REFERENCES:
                    raise KeyError(f"unknown reference {key}")
                if key not in self.order:
                    self.order.append(key)
                nums.append(self.order.index(key) + 1)
            return ", ".join(f"[{n}]" for n in nums)

        return re.sub(r"\[@([a-z0-9_,\s]+)\]", repl, text)


def fit(path, max_w=6.0, max_h=7.6):
    """Width that fits an image inside max_w x max_h inches, preserving aspect ratio."""
    w, h = Image.open(path).size
    width = min(max_w, max_h * w / h)
    return Inches(width)


def pct(v):
    return f"{v * 100:.1f}%"
