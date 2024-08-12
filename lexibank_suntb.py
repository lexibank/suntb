from pathlib import Path

import attr
import pylexibank
from clldutils.misc import slug


@attr.s
class CustomLanguage(pylexibank.Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default="Sino-Tibetan")


@attr.s
class CustomConcept(pylexibank.Concept):
    Chinese_Gloss = attr.ib(default=None)
    Number = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    dir = Path(__file__).parent
    id = "suntb"
    writer_options = dict(keep_languages=False, keep_parameters=False)

    language_class = CustomLanguage
    concept_class = CustomConcept
    form_spec = pylexibank.FormSpec(
        separators=";,/",
        missing_data=("*", "---", "-", "--"),
        replacements=[(" ", "_")],
        brackets={"[": "]", "(": ")"},
    )

    def cmd_download(self, args):
        self.raw_dir.write("sources.bib", pylexibank.util.getEvoBibAsBibtex("Sun1991"))

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
        for entry in pylexibank.progressbar(
            self.raw_dir.read_csv("ZMYYC.csv", delimiter="\t", dicts=True)
        ):
            args.writer.add_forms_from_value(
                Language_ID=language_lookup[entry["language"]],
                Parameter_ID=concept_lookup.get(entry["srcid"].split(".")[0]),
                Local_ID=entry["rn"],
                Value=entry["reflex"],
                Source=["Sun1991"],
            )
