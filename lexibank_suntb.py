from pathlib import Path

import attr
from clldutils.misc import slug
from pylexibank import FormSpec
from pylexibank import Language, Concept
from pylexibank import progressbar
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import getEvoBibAsBibtex


@attr.s
class CustomLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default="Sino-Tibetan")


@attr.s
class CustomConcept(Concept):
    Chinese_Gloss = attr.ib(default=None)
    Number = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "suntb"
    language_class = CustomLanguage
    concept_class = CustomConcept
    form_spec = FormSpec(
        separators=";,/", missing_data=("*", "---", "-", "--"), brackets={"[": "]", "(": ")"}
    )

    def cmd_download(self, args):
        self.raw_dir.write("sources.bib", getEvoBibAsBibtex("Sun1991"))

    def cmd_makecldf(self, args):

        args.writer.add_sources()
        language_lookup = args.writer.add_languages(lookup_factory="Name")

        concept_lookup = {}
        for concept in self.conceptlists[0].concepts.values():
            idx = concept.id.split("-")[-1] + "_" + slug(concept.english)
            concept_lookup[concept.english] = idx
            concept_lookup[concept.number] = idx
            args.writer.add_concept(
                ID=idx,
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
                Name=concept.english,
                Chinese_Gloss=concept.attributes["chinese"],
            )
        for entry in progressbar(self.raw_dir.read_csv("ZMYYC.csv", delimiter="\t", dicts=True)):
            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["language"]],
                Parameter_ID=concept_lookup.get(entry["srcid"].split(".")[0]),
                Local_ID=entry["rn"],
                Value=entry["reflex"],
                Source=["Sun1991"],
            )
