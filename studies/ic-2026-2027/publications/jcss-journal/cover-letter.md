# Cover letter — JCSS journal version

Final letter of 29 October 2026, incorporating the advisor's editorial
recommendations, the institutional scholarship confirmed by Davi on 22 October
and the factual ethics statement confirmed by Davi on 29 October.
Paste into the portal only the text between the two rules, as plain text.
Update the date if the submission happens on another day. Check the final
letter against the 450-word limit.

---

31 October 2026

Professor Takashi Kamihigashi
Editor-in-Chief, Journal of Computational Social Science

Dear Professor Kamihigashi,

Please consider our manuscript "Limits of Detecting Network Influence in Attitude Panels" for publication as a research article.

Attitude panels record responses without observing social contacts, making it difficult to distinguish network influence from individual persistence. Our prespecified simulation investigates the limits of this discrimination with explicit measurement error and persistence models matched to short-term stability. In panels approximating the Swiss Household Panel's size and refreshment design, a fixed long-lag classifier first reached an AUC of 0.70 against trait-plus-autoregressive persistence at nominal innovation-variance fractions of 0.10 for reliabilities from 0.55 to 0.90, and 0.30 at reliability 0.50.

The contribution extends beyond these numerical boundaries. The prespecified comparison across all persistence models was not interpretable under its eligibility rules, and subsequent exploratory analyses show how strongly discrimination depends on the comparison design. A changing response channel separated panels without influence; allowing persistence to fit reliability and one additional lag absorbed most separation by a lag-four-and-five classifier, with reliability shifts of only 0.0011 to 0.0028. The article distinguishes these demonstrated sensitivities from the untested effects of richer persistence and network burn-in. It establishes conditional discrimination limits rather than identifying social influence in observed data.

Protocol, code and reading rules were frozen before the confirmatory run, which used new seeds after partial exposure to calibration results. The paper separates confirmatory findings, exploratory analyses and later interpretations. Section 3.7 summarizes generative-AI use, with the detailed roles and verification record in Online Resource 1. The authors take full responsibility for the scientific content and conclusions.

Code, protocol, released outputs and the earlier rule-assembled manuscript are archived at https://doi.org/10.5281/zenodo.23418473; that manuscript is disclosed as a preprint. In the archive, code and data are under the MIT License and manuscript texts and figures under CC BY 4.0. Two Online Resources document the full record and all 414 analysis units, including reproduction limits.

The manuscript is not under consideration elsewhere, and both authors approved its submission. The authors have no competing interests. The first author received an institutional undergraduate research scholarship from Inteli – Instituto de Tecnologia e Liderança. The empirical anchor is a secondary analysis of anonymized SHP microdata obtained under a data-use contract, without contact with participants and with only aggregates reported; no ethics committee review was sought.

Sincerely,

Davi Abreu da Silveira, on behalf of both authors
Inteli – Instituto de Tecnologia e Liderança, São Paulo, Brazil
davi.silveira@sou.inteli.edu.br

---

## Sources of the letter's facts

| Statement                                                               | Source                                                                                                                                |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Editor-in-Chief: Takashi Kamihigashi                                    | Official editorial-board page, link.springer.com/journal/42001/editorial-board, checked 13 October 2026                               |
| Panel geometry and nominal innovation-variance fraction                 | Methods, synthetic panels and network influence; Online Resource 1, Sections S2, S3 and S8                                            |
| Boundaries 0.10 at r = 0.55–0.90 and 0.30 at r = 0.50                   | `j.b.r055.first.point` through `j.b.r090.first.point`, `j.b.r050.first.point`; Results and Table `tab:boundaries-B`                   |
| Prespecified comparison across persistence models unavailable           | Results, other persistence models; Online Resource 1, Sections S3–S5                                                                  |
| Response drift separates panels without influence                       | `j.x5.trend003.min`, `j.x5.trend003.max`; exploratory Results and Table `tab:exploratory`                                             |
| Combined additional-lag/free-reliability fit, with shifts 0.0011–0.0028 | `j.x3.known.auc.min`/`.max`, `j.x3.free.auc.min`/`.max`, `j.x3.free.r_shift.min`/`.max`; exploratory Results and Discussion           |
| Unchanged protocol and results; exposure and new seeds                  | Methods; Online Resource 1, Sections S4 and S12                                                                                       |
| AI roles, responsibility and verification limits                        | Methods 3.7; Online Resource 1, Sections S4, S9 and S11                                                                               |
| Archive DOI, preprint and licence coverage                              | Data and code availability                                                                                                            |
| 414 analysis units                                                      | `v4.protocol.units.all`; Results and Online Resource 2                                                                                |
| Funding, competing interests and ethics                                 | Statements and Declarations; Davi confirmed the Inteli institutional scholarship on 22 October 2026 and the factual ethics statement on 29 October 2026 |

The letter does not claim that every supplementary table can be regenerated
from the archived aggregates or that the full release was reproduced
independently. Suggested reviewers and the suggested handling editor are
entered from the private coordination file, outside this repository.
