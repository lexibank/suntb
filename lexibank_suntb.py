from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import *
from clldutils.text import split_text
from pylexibank.dataset import Dataset as BaseDataset, Language
from pylexibank.util import getEvoBibAsBibtex
from tqdm import tqdm
import lingpy as lp
from pyclts import TranscriptionSystem 
import attr

@attr.s
class HLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    ChineseName = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "suntb"
    language_class = HLanguage

    def clean_form(self, item, form):
        if form not in ["*", "---", "-", "", "--"]:
            forms = split_text(form, separators=";,/")
            if forms:
                form = strip_brackets(forms[0])
                return form.replace(" ", "_").replace("__", "_").strip("!").strip("?").strip("_")

    def cmd_install(self, **kw):

        with self.cldf as ds:
            ds.add_sources()
            langs = {}
            for language in self.languages:
                ds.add_language(
                        ID=language['ID'],
                        Glottocode=language["Glottocode"],
                        Name=language["Name"],
                        Latitude=language['Latitude'],
                        Longitude=language['Longitude'],
                        SubGroup=language['SubGroup'],
                        Family='Sino-Tibetan'
                    )
                langs[language["Name"]] = language['ID']

            # add concepts, first from the local list, then from the conceptlist
            # (this is necessary because this data is a partial subset of the
            # Sun-1991 conceptlist in Concepticon, even tough it should refer to
            # the same source, and we don't want to apport changes there, at least
            # for the time being)
            concept_map = {}
            for concept in self.concepts:
                # if there is an ID, we were able to map the
                # different gloss to Sun-1991 list and we just need to
                # store this mapping; in the fewer cases this did not happen,
                # we add the concept to the dataset specific list of concepts
                if concept["ID"]:
                    concept_map[concept["ENGLISH"]] = concept["CL_ENGLISH"]
                else:
                    ds.add_concept(
                        ID=slug(concept["ENGLISH"]),
                        Concepticon_ID=concept["CONCEPTICON_ID"],
                        Name=concept["ENGLISH"],
                        Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                    )

            ds.add_concepts(id_factory=lambda c: slug(c.label))

            # add lexemes
            for entry in tqdm(self.raw.read_tsv("ZMYYC.csv")[1:], desc="cldfify"):
                # extract fields from row; we replace glosses commas
                # (avoiding escape problems and difficulties) and
                # check whether the current gloss is an alias
                reflex, gloss, language = entry[1], entry[2], entry[6]
                gloss = gloss.replace(",", ";")

                if gloss in concept_map:
                    gloss = concept_map[gloss]

                ds.add_lexemes(
                    Language_ID=langs[language],
                    Parameter_ID=slug(gloss),
                    Value=entry[1],
                    Source=["Sun1991"],
                )

    def cmd_download(self, **kw):
        if not self.raw.exists():
            self.raw.mkdir()
        self.raw.write("sources.bib", getEvoBibAsBibtex("Sun1991", **kw))
