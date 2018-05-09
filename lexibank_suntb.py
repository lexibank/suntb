# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.path import Path
from clldutils.misc import slug
from pylexibank.dataset import Metadata
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import getEvoBibAsBibtex

from clldutils.text import split_text
import re

class Dataset(BaseDataset):
    dir = Path(__file__).parent

    def cmd_install(self, **kw):

        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())
            # add languages
            language_map = {}
            for language in self.languages:
                ds.add_language(
                    ID=slug(language['NAME']),
                    Glottocode=language['GLOTTOCODE'],
                    Name=language['NAME'],
                )

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
                if concept['ID']:
                    concept_map[concept['ENGLISH']] = concept['CL_ENGLISH']
                else:
                    ds.add_concept(
                        ID=slug(concept['ENGLISH']),
                        Concepticon_ID=concept['CONCEPTICON_ID'],
                        Name=concept['ENGLISH'],
                        Concepticon_Gloss=concept['CONCEPTICON_GLOSS'],
                    )

            for gloss, concept in self.conceptlist.concepts.items():
                ds.add_concept(
                    ID=slug(concept.english),
                    Name=concept.english,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss,
                )

            # add lexemes
            for entry in self.raw.read_tsv('ZMYYC.csv')[1:]:
                # extract fields from row; we replace glosses commas
                # (avoiding escape problems and difficulties) and
                # check whether the current gloss is an alias
                reflex, gloss, language = entry[1], entry[2], entry[6]
                gloss = gloss.replace(',', ';')

                if gloss in concept_map:
                    gloss = concept_map[gloss]

                # with the exception of indications of Chinese loanwords,
                # treated here, all parentheses actually contain sound
                # information, so we should keep them; after that, remove
                # only parentheses (and the information in between)
                reflex = reflex.replace('(Ch.)', '')
                reflex = reflex.replace('(', '')
                reflex = reflex.replace(')', '')

                # remove doubt marks
                reflex = reflex.replace('???', '')
                reflex = reflex.replace('??', '')

                # remove elipsis
                reflex = reflex.replace('...', ' ')

                for form in split_text(reflex, separators=';/'):
                    # remove multiple spaces; leading&trailing
                    form = re.sub('\s+', ' ', form).strip()

                    # skip over if empty entry
                    if form == '*':
                        continue

                    # comment out once a profile is made
                    #tokens = self._tokenizer("IPA", form)

                    for row in ds.add_lexemes(
                        Language_ID=slug(language),
                        Parameter_ID=slug(gloss),
                        Value=form,
                        Source=['Sun1991'],
                    ):
                        pass

    def cmd_download(self, **kw):
        if not self.raw.exists():
            self.raw.mkdir()
        self.raw.write('sources.bib', getEvoBibAsBibtex('Sun1991', **kw))
