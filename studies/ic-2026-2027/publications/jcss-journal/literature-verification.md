# Literature verification for the merged Section 2 (agent L, 2026-10-13)

Worktree `docs/jcss-journal-lit-20261013`; files changed: `sections/background.tex`,
`sections/related-work.tex` (now a one-line stub), `references.bib`.

## How sources were checked

- Metadata: Crossref works API (`https://api.crossref.org/works/<DOI>`) unless stated
  otherwise; DataCite for DataCite DOIs; arXiv API (`export.arxiv.org/api/query`);
  OpenReview API; NBER chapter PDF; Open Library and Internet Archive catalog records
  for the 1955 book; the Guilford Press catalog page for the 2006 book.
- Content: open full text where reachable (PMC/Europe PMC, arXiv, author or society
  repositories, IEEE open access, Sociological Science, NBER, Internet Archive for the
  openly accessible scan of the 1943 Annals issue, because Project Euclid, where the article is open access, blocked this client). Otherwise abstracts from Crossref, Europe PMC,
  RePEc/IDEAS or OpenAlex (abstract field reconstructed from its inverted index).
- Blocked for this agent (HTTP 403, bot challenges): JSTOR, Project Euclid (direct),
  Taylor & Francis, Springer Link, ScienceDirect, OUP Academic, AgEcon Search, the CSIC
  repository. The Chrome extension was not connected, so no browser route was used. No
  restricted (lending-only) Internet Archive item was opened.
- Quotes below are kept to short fragments; locators point to the passage read.
- Style note: `sn-mathphys-num.bst` keeps only digits in `pages` (an e-locator
  `e2408163122` prints as `2408163122`) and never prints `url` for `@article`.
  Alphanumeric article numbers therefore go in `note` ("Article e…"), and a JASSS
  article without DOI gets its URL in `note`.

## A. References added (keys reserved in plan §9 unless noted)

### christakis2007

- Metadata: Crossref 10.1056/NEJMsa066082 (NEJM 357(4):370–379, 2007). Europe PMC PMID 17652652.
- Read: abstract (Europe PMC).
- Claim: obesity appears to spread through social ties in the Framingham Heart Study network. Abstract, Conclusions ("obesity appears to spread through social ties"); Methods name the Framingham Heart Study network.
- Status: verified (abstract).

### cohencole2008

- Metadata: Crossref 10.1136/bmj.a2533 (BMJ 337:a2533, 2008); author full names from Europe PMC (PMC2600605).
- Read: abstract (Europe PMC).
- Claim: with standard network-study models, "network effects" appear for acne, headaches and height and become smaller and insignificant after adjustment for environmental confounders. Abstract, Results (last sentence).
- Status: verified (abstract). Article number given in `note`.

### aral2009

- Metadata: Crossref 10.1073/pnas.0908800106 (PNAS 106(51):21544–21549, 2009).
- Read: abstract (Europe PMC, PMC2799846).
- Claim: matched-sample estimation attributes more than half of perceived contagion in product adoption to homophily. Abstract (homophily explains >50% of perceived behavioral contagion; 27.4 million users, mobile service adoption).
- Status: verified (abstract).

### vanderweele2011

- Metadata: Crossref 10.1177/0049124111404821 (SM&R 40(2):240–255, 2011).
- Read: abstract (Europe PMC, PMC4288024).
- Claim: sensitivity analysis assesses how far latent homophily or confounding could explain away contagion effects. Abstract, sentences 3–4.
- Status: verified (abstract).

### steglich2010

- Metadata: Crossref 10.1111/j.1467-9531.2010.01225.x (Sociological Methodology 40(1):329–393, 2010). Crossref title carries a chapter prefix "8."; dropped.
- Read: abstract (Crossref).
- Claim: stochastic actor-oriented models separate selection (homophilous partner choice) from influence with network and behavior observed in panel waves. Abstract (separating the two effects; three-wave school panel).
- Status: verified (abstract).

### snijders2010

- Metadata: Crossref 10.1016/j.socnet.2009.02.004 (Social Networks 32(1):44–60, 2010).
- Read: Crossref record and the SIENA project's article list (describes it as a tutorial); no abstract available.
- Claim: cited jointly with steglich2010 as the reference for stochastic actor-oriented models (introduction/tutorial). No further content attributed.
- Status: metadata only for content (title-level use).

### bramoulle2009

- Metadata: Crossref 10.1016/j.jeconom.2008.12.021 (J. Econometrics 150(1):41–55, 2009).
- Read: abstract (RePEc/IDEAS).
- Claim: with interactions structured by a known social network, endogenous and exogenous effects in an extended linear-in-means model are generally identified, although identification may fail for particular structures. Abstract, sentences 2 and 5.
- Status: verified (abstract).

### lewbel2023

- Metadata: Crossref 10.1086/722090 (JPE 131(4):898–946, 2023).
- Read: abstract (RePEc/IDEAS).
- Claim: linear social network models are point-identified without observed links, from many small networks with known membership in which each person is observed once (e.g., classrooms). Abstract, sentences 1–2.
- Status: verified (abstract).

### depaula2024 (key reserved; volume year is 2025)

- Metadata: Crossref 10.1093/restud/rdae088 (Review of Economic Studies 92(4):2691–2729; online 2024-09-03, print 2025-07-07). `year = {2025}`; key kept as reserved.
- Read: published abstract (Crossref) and the arXiv version linked to that DOI (arXiv:1910.07452v4), §1 (model, footnote 4), §2 (assumptions: N fixed and repeated), estimation section (sparsity; rate depends on T relative to dN; requirement NT ≫ dN(N−1)+K), simulations (N = 30, 65, 70; T from 5).
- Claims: identifies the full interaction matrix of a linear (canonical) social interactions model from panel data when the network is constant over time; estimator needs many periods relative to the number of ties per unit. Abstract; arXiv v4 estimation section.
- Status: verified (published abstract; full text of the arXiv version).

### heckman1981

- Metadata: NBER chapter PDF (Studies in Labor Markets, ed. S. Rosen, University of Chicago Press, 1981, pp. 91–140); chapter URL https://www.nber.org/chapters/c8909.
- Read: full text (NBER PDF), pp. 91–95 and note 1.
- Claims: true state dependence (experience changes later preferences, prices or constraints) versus spurious state dependence (past experience proxies for persistent unobserved differences). pp. 91–92. Heckman also names Feller (1943) as seminal on the problem (p. 93).
- Status: verified (full text).

### feller1943

- Metadata: Crossref 10.1214/aoms/1177731359 (Ann. Math. Stat. 14(4):389–400, 1943).
- Read: full text via the Internet Archive scan of the December 1943 issue (item `sim_annals-of-mathematical-statistics_1943-12_14_4`, OCR text; not lending-restricted), §1 Introduction (p. 389) and §5 "The nature of contagion" (p. 398).
- Claims: the same distribution arises from true contagion and from apparent contagion due to population inhomogeneity (p. 389); deciding requires "a detailed study of the correlation between various time intervals" (p. 398), not the distribution of events alone.
- Status: verified (full text).

### blumen1955

- Metadata: Open Library edition OL6193430M and Internet Archive catalog record `industrialmobili0000isad`: Blumen, Kogan and McCarthy, _The Industrial Mobility of Labor as a Probability Process_, Cornell Studies in Industrial and Labor Relations v. 6, Ithaca: Cornell University, 1955 (LCCN 55062561). The scan itself is lending-restricted and was not opened.
- Read: catalog records; Goodman (1961) abstract, which refers to the mover–stayer estimators used by Blumen, Kogan and McCarthy.
- Claim: cited with goodman1961 for mover–stayer models of labor mobility. The model's definition is attributed through goodman1961.
- Status: metadata verified; content checked only through goodman1961 (secondary).

### goodman1961

- Metadata: Crossref 10.1080/01621459.1961.10482130 (JASA 56(296):841–868, 1961).
- Read: abstract (OpenAlex).
- Claim: mover–stayer model = stayers who remain in one category plus movers following a Markov chain. Abstract, sentence 1.
- Status: verified (abstract).

### zaller1992

- Metadata: Crossref 10.2307/2111583 (AJPS 36(3), first page 579). Last page 616: Crossref lists only the first page; the next article in the issue starts at p. 617 (Crossref issue listing), consistent with 579–616.
- Read: abstract (OpenAlex).
- Claim: most people are internally conflicted over most political issues and answer from whatever ideas are at the top of their heads. Abstract, sentence 3.
- Status: verified (abstract); page range inferred as described.

### ansolabehere2008

- Metadata: Crossref 10.1017/S0003055408080210 (APSR 102(2):215–232, 2008).
- Read: abstract (Crossref).
- Claim: averaging many items on the same issue area removes much measurement error and reveals stable preferences. Abstract, sentence 3.
- Status: verified (abstract).

### vaiseykiley2021

- Metadata: Crossref 10.15195/v8.a5 (Sociological Science 8:83–95, 2021).
- Read: full text (open access PDF), p. 83.
- Claim (cited with kiley2020): most survey responses in GSS three-wave panels reflect settled dispositions. Abstract, last sentence.
- Status: verified (full text).

### mcpherson2001

- Metadata: Crossref 10.1146/annurev.soc.27.1.415 (Annu. Rev. Sociol. 27:415–444, 2001).
- Read: abstract (Crossref).
- Claim: people form ties with similar others (homophily). Abstract, sentences 1–2.
- Status: verified (abstract).

### takacs2016

- Metadata: Crossref 10.1371/journal.pone.0157948 (PLOS ONE 11(6):e0157948, 2016).
- Read: abstract (Europe PMC, PMC4917087).
- Claims: evidence for negative influence is mixed; in one experiment and one further study, discrepancy or disliking did not produce negative shifts; shifts grew linearly with opinion distance. Abstract, sentences 3–6.
- Status: verified (abstract). Article number given in `note`.

### grimm2005

- Metadata: Crossref 10.1126/science.1116681 (Science 310(5750):987–991, 2005).
- Read: abstract (Europe PMC, USGS publication record). Full text not reachable (publisher; CSIC repository behind a bot challenge).
- Claim: pattern-oriented modeling is a general strategy for designing, testing and analyzing agent-based models. Abstract, sentence 3. The mapping to our design (short-lag pattern matched, longer-lag pattern tested) is our reading and is worded as such.
- Status: verified (abstract only).

### lopezpaz2017

- Metadata: OpenReview SJkXfE5xx ("ICLR 2017 Poster"); arXiv:1610.06545v4 first page states publication at ICLR 2017. Entry type `inproceedings`, URL to OpenReview.
- Read: arXiv v4 abstract and introduction.
- Claim: under the null of equal distributions, held-out classifier accuracy stays near chance; departure from chance indicates differences the classifier can use. Abstract; Introduction, paragraph 2.
- Status: verified (full text of the arXiv version).

### kim2021classifier

- Metadata: Crossref 10.1214/20-AOS1962 (Ann. Statist. 49(1):411–434, 2021).
- Read: abstract (Crossref, identical to arXiv:1602.02210v4).
- Claims: accuracy-based tests are consistent whenever the true error stays better than chance; in a high-dimensional Gaussian mean-difference setting the LDA-based test is worse than Hotelling's by a constant factor (ARE 1/√π for balanced samples). Abstract, sentences 3 and 6.
- Status: verified (abstract).

### robert2011

- Metadata: Crossref 10.1073/pnas.1102900108 (PNAS 108(37):15112–15117, 2011).
- Read: abstract (Europe PMC, PMC3174657).
- Claim: ABC model choice with insufficient summary statistics loses information, and its approximation error may be unrelated to computational effort. Abstract, sentences 4–5.
- Status: verified (abstract).

### gourieroux1993

- Metadata: Crossref 10.1002/jae.3950080507 (J. Appl. Econometrics 8(S1):S85–S118, 1993). The style prints the pages as 85–118 (digits only); issue S1 is printed.
- Read: abstract (RePEc/IDEAS; same text via OpenAlex).
- Claim: indirect inference estimates the parameters of a model that only needs to be simulable, through an auxiliary criterion and a simulation step. Abstract, sentences 1–3 and 5.
- Status: verified (abstract).

### kennykashy2006 (for writer F, methods actor–partner sentence; not cited in Section 2)

- Metadata: Guilford Press catalog page (Kenny, Kashy and Cook, _Dyadic Data Analysis_, Methodology in the Social Sciences series, copyright 2006; publisher address New York).
- Read: publisher description and table of contents (chapter 7, the Actor–Partner Interdependence Model).
- Claim available to writers: a standard reference for actor and partner effects in dyadic data (APIM, ch. 7).
- Status: verified (publisher page).

## B. Existing entries changed

- `coding2024`: a peer-reviewed version now exists. IEEE Transactions on Computational Social Systems, early access, DOI 10.1109/TCSS.2026.3738519 (Crossref record created 2026-10-08; IEEE abstract API: volume "PP", pages 1–13 provisional, open access CC BY 4.0). Entry converted from `@misc` (arXiv v3) to `@article`, `year = {2026}`, `note = {Early access}`, no pages (pagination not final). Full text read (IEEE PDF): Keep baseline reaches high overall F1 with change F1 equal to zero (§VI, microlevel evaluation; Conclusion); "on real world data they often fail to outperform trivial baselines" (Conclusion). Both claims used in Section 2 and in the old Introduction are supported by the published version. Status: verified (full text). The text no longer calls it a preprint.
- `dang2026`, `achitouv2026`, `urena2026`: no peer-reviewed version found (arXiv API: no journal_ref/DOI; Crossref and OpenAlex title searches 2026-10-13; Dang and Ma also on PsyArXiv). Kept as `@misc` with `note = {Preprint, arXiv:…v1}`; duplicated abs URL removed; editorial notes removed ("version 1; no journal DOI confirmed"). Claims re-read today: dang2026 abstract (power depends jointly on reliability, ICC, waves, sample size, effect size); urena2026 full text (likelihood of trajectories given a known adjacency matrix and fully observed binary states, Eq. 3; "Independent" mechanism among six candidates; model selection can fail, abstract). achitouv2026 is no longer cited in the main text.
- `stadtfeld2020`: author `{van Duijn}, Marijtje`. Scenario checked (see §D).
- `gelastopoulos2025`: author `{van de Rijt}, Arnout`; article number moved to `note = {Article e2408163122}` (Crossref article-number e2408163122). Scope checked (see §D).
- `manski1993`: statement checked (see §D); entry unchanged except the url removal.
- `friedkin1990`: issue `3--4` (en dash).
- `hegselmann2002`, `lorenz2006`: no DOI (Crossref search); URL moved to `note = {\url{…}}` so it prints; both URLs resolve (HTTP 200).
- Title capitals protected: `proskurnikov2017/2018` ({Part I}, {Part II}); `poses2021` ({European Social Survey}); `hout2016` ({General Social Survey}); `carpentras2022` ({Deffuant}); `hill2001` ({Converse's} ``Black-and-White'', matching the Crossref title's quotation marks); `zachrison2016` ({An} after the question mark); `voorpostel2025shp` ({Swiss Household Panel}); `stauffer2000` ({Sznajd}); `lorenz2006` ({Hegselmann--Krause}); `maes2013` ({Explaining}).
- Name particles: `stauffer2000` `{Moss de Oliveira}` (was printed as "Oliveira, S."), plus the two above.
- `xu2021sensitivity`: note "Published online 2020-10-19" removed.
- `converse1964`: the 2006 reprint DOI no longer sits in the 1964 chapter's `doi` field (it printed as if it were the chapter's DOI, and the chapter type also printed it twice); it now appears inside the reprint note (Critical Review 18(1–3):1–74, 2006; Crossref 10.1080/08913810608443650); `address = {New York}` added (Internet Archive catalog record of _Ideology and Discontent_: New York, Free Press, 1964). Chapter pages 206–261 kept, not re-checked (book restricted).
- `maes2013`: article number moved to note (uncited).
- Duplicated DOI URLs: removed `url = {https://doi.org/<same DOI>}` from 69 entries by script; the script compared each removed URL with the entry's `doi` field and changed nothing else (key list and all other fields identical before and after). For `@incollection`, `@book` and `@inproceedings` entries this removes the DOI printed twice (moor2026, sirbu2016, alwin2007, lenti2024, kenny2001starts, converse1964). Keys: degroot1974 friedkin1990 deffuant2000 castellano2009q sznajd2000 nowak1990 castellano2009 suchecki2005 flache2017 sasahara2021 gestefeld2023 banisch2024 hegselmann2023 clifford1973 holley1975 stauffer2000 lorenz2007 sirbu2016 proskurnikov2017 proskurnikov2018 jager2005 maes2013 holme2006 kiley2020 lersch2023 heise1969 wiley1970 achen1975 alwin2007 alwinkrosnick1991 hout2016 poses2021 moor2026 carpentras2023 manski1993 shalizi2011 kustov2021 mulder2023 stadtfeld2020 lucas2023 lucasdonnellan2012 hill2001 hillkriesi2001 converse1964 bollen2021 aichholzer2013 kraemer2025 granger1976 gelastopoulos2025 borile2026 carpentras2022 daza2021 zachrison2016 kim2024 lenti2024 antoun2026 tang2025empirical xu2021sensitivity advani2018credibly kenny1995tse kenny2001starts cole2005tso ludtke2018starts hamaker2015critique devine2024trust schuurman2019reliability lang2026joint turper2017 lugtig2017.
- Rendering checked by compiling a scratch document with `sn-jnl` (both `iicol` and one-column) and `sn-mathphys-num.bst`: no BibTeX warnings; e-locators, particles, capitals, en dashes and the JASSS URLs print as intended.

## C. Existing references cited in the new Section 2: claim support

Rechecked today (abstract or full text):

- `flache2017`: C02, C31 (open JASSS full text, earlier ledger); three classes of influence; call for empirical tests of micro-level assumptions. Unchanged support.
- `gestefeld2023`: JASSS full text re-read today: SHP trust in government on a yearly basis over 11 years; no information about the communication of individuals (§7.9 area). Verified.
- `moor2026`: arXiv:2602.00876v1 re-read today: minimum opinion drift before explained variance exceeds the no-change null (§3.1, Experiment 1); optimizer "freezes" to mimic the null (§3.2, Experiment 2), also under added process noise (§3.3; noise added to each generated distribution before it feeds the next step). Published chapter not read (Springer blocked); title and pages from Crossref.
- `carpentras2022`: published abstract: robust to binning, not to noise and distortions. Verified.
- `carpentras2023`: published abstract plus earlier full-text locator (p. 227, ledger R31) for the incompatibility claim.
- `achen1975`: abstract (Crossref): nearly all inconsistency from vague questions. Verified.
- `hill2001`: abstract (Crossref): extends Converse's black-and-white model with a group of rational/durable changers; results undermine the measurement-error model; four time points, Swiss panel. Verified.
- `converse1964`: claim (black-and-white model; unstable group answering essentially at random) checked only through the Hill and Kriesi abstracts (APSR 2001; Political Analysis 2001). Primary text not reachable (T&F 403; Internet Archive copies lending-restricted). Status: secondary check only; flag for the coordinator.
- `hout2016`: abstract: 293 core items; 62 above 0.85 and 71 between 0.70 and 0.85 (so 133 above 0.70); 15 below 0.40. Verified.
- `poses2021`: abstract: measurement quality = share of response variance explained by the latent trait; question averages range 0.25–0.88; overall 0.65. Verified.
- `heise1969`, `wiley1970`: no abstract and no reachable full text; the sentence says only what the titles state (separating stability from reliability; estimating measurement error in panel data). Status: metadata/title level, as in the earlier ledger (C36).
- `kenny1995tse`: earlier full-text check (ledger R60/Q7, p. 53). `cole2005tso`, `ludtke2018starts`: abstracts re-read today (Europe PMC): improper solutions with few waves or small N; frequent nonconvergence and inadmissible STARTS estimates. Verified.
- `lucas2023`: abstract re-read today (Crossref): with realistic assumptions the CLPM is very likely to find spurious cross-lagged effects. `hamaker2015critique`: earlier full-text check (Q7). Verified.
- `kiley2020`: published abstract (most observed change is short-term change or measurement error) and the OSF author version re-read today (BIC comparisons; updating between every wave indistinguishable from settled dispositions with high measurement error). Verified.
- `lersch2023`: abstract re-read today (persistent life-course change; substantial year-to-year fluctuation; six panels incl. SHP); three-wave identification claim from the earlier full-text check (ledger R35, pp. 222, 228).
- `mulder2023`: abstract (OpenAlex): RI-CLPM power analysis for sample size and number of repeated measures, with a measurement-error extension (STARTS). Verified (abstract).
- `alwinkrosnick1991` (newly cited): abstract (OpenAlex): intracohort comparisons of party identification support the aging-stability hypothesis. Verified (abstract).
- `granger1976` (newly cited): abstract/summary (OpenAlex): the sum of two or more series most likely follows a mixed ARMA model; aggregates measured with error give mixed models. Verified (abstract).
- `shalizi2011`: abstract re-read today: homophily, contagion and covariate effects are generically confounded. Verified.
- `zachrison2016`, `daza2021`: earlier ledger R42 (methods sections). `xu2021sensitivity`, `advani2018credibly`: abstracts re-read today (error and bias in observed networks; missing network data and endogenous formation). Verified.
- `soni2019rankers`: earlier ledger R68 (official PMLR PDF). `lang2026joint`: arXiv v2 abstract re-read today (joint inference of network and interaction kernel from multiple trajectories); published record via Crossref. Verified.
- `tang2025empirical`: published abstract re-read today: in longitudinal field data on adolescents, negative influence and assimilation are significant for rap/hip-hop clothing-style preferences, with little weight for bounded confidence. Verified (abstract).
- `lenti2024`, `borile2026`: published abstracts re-read today: likelihood-based estimation outperforms simulation-based estimation for the bounded-confidence model; joint estimation of confidence bound and convergence rate has identifiability issues in parts of the parameter space. Verified (abstracts).
- `degroot1974`, `friedkin1990`, `deffuant2000`, `hegselmann2002`, `jager2005`: one-sentence descriptions rest on the earlier ledger rows C03, C05, C16, C18, C22 (primary or open copies read then). Not re-read today.

## D. Precise statements requested

- Manski 1993 (`manski1993`). Read: published abstract (RePEc/IDEAS record of the RES article) and the 1991 working-paper abstract (RePEc); full text not reachable. Statement: without prior information on the composition of reference groups, the distribution of behavior cannot show whether a group's average behavior affects its members; even with known reference groups, inference is "difficult to impossible" when the variables that define groups and those that directly affect outcomes are functionally dependent or statistically independent (published abstract). The linear-in-means setting is the paper's framework according to de Paula et al. (arXiv v4, §1, footnote 4) and Bramoullé et al. (abstract), but it is not in the abstract; Section 2 therefore attributes "linear-in-means" only to Bramoullé et al.
- Gelastopoulos, Sage and van de Rijt 2025 (`gelastopoulos2025`). Read: full text (PMC12167982), "Generalization" section and its theorems, plus the abstract. Scope: for any stochastic process describing longitudinal observations (a unit's sequence, or a vector for a group), there exist a pure reinforcement model (each observation a measurable function of past observations and i.i.d. noise) and a pure heterogeneity model (a function of a latent variable and i.i.d. noise) with the same joint distribution. The functional forms are unrestricted and may change with n; the result is existence of a twin, not a statement about any parametric family. Their parsimony argument for stationary heterogeneity models needs exchangeable data. The abstract's phrase "any longitudinal data with systematic differences" is the authors' own and matches the theorem's generality, but it should be read as "any joint distribution, with unrestricted models".
- Stadtfeld et al. 2020 (`stadtfeld2020`). Read: full text (published version deposited on the SIENA site), pp. 1110–1117. Scenario: research setting 1, a fictitious study of friendship and three-category opinions (negative, neutral, positive) in four communities of 120 actors, simulated from a stochastic actor-oriented model with influence (total similarity) parameter 0.8 and homophily 1.5 (Table 1); 200 data sets per design; power = share of data sets in which the parameter is significant at p < .05. With two waves and 30 actors the influence effect had power 10.0% (homophily 34.5%); with five waves and 120 actors 97.5% (Table 4, p. 1116; text p. 1116). The old ledger locator "p. 1115" should read p. 1116.
- Feller 1943 (`feller1943`). The Greenwood–Yule/Pólya–Eggenberger distribution arises both from true contagion and from apparent contagion due to inhomogeneity; the event distribution alone cannot decide, the correlation between time intervals is needed (pp. 389, 398).

## E. Considered but not added

- `granger1980` (Granger, Long memory relationships and the aggregation of dynamic models, J. Econometrics 14(2):227–238; Crossref metadata confirmed): dropped. The article has no abstract (Crossref, RePEc, Elsevier API) and the full text was not reachable, so its content (aggregation of heterogeneous AR processes gives long memory) could not be checked. Writers must not cite it. Section 2 uses `granger1976` (verified) for multi-timescale persistence.
- `krosnick1995` (Krosnick and Petty, Attitude strength: An overview): not added; not needed in Section 2 and no checkable abstract or chapter text was reached (the 2014 Psychology Press reprint of the book is DOI 10.4324/9781315807041). Writers must not cite it unless it is verified later.
- Not used for word-budget or scope reasons (no entry created): Converse 1970; Sturgis, Allum and Brunton-Smith 2009; Warren and Halpern-Manners 2012; Saris and Gallhofer 2014; Huckfeldt and Sprague 1995; Zuckerman, Dasović and Fitzgerald 2007; Sobkowicz 2009; Lorenz, Neumann and Schröder 2021; De et al. 2016; Cranmer, Brehmer and Louppe 2020; McFadden 1989.

## F. Entries that became uncited after the rewrite (kept in references.bib)

banisch2024, lorenz2007, sirbu2016, proskurnikov2017, proskurnikov2018, alwin2007,
achitouv2026, hillkriesi2001, schuurman2019reliability, devine2024trust, turper2017,
lugtig2017 (the last three remain relevant to the SHP anchor in the Discussion or
Online Resource 1). Already uncited before: castellano2009q, sznajd2000, nowak1990,
castellano2009, suchecki2005, sasahara2021, hegselmann2023, clifford1973, holley1975,
stauffer2000, lorenz2006, maes2013, holme2006, kustov2021, bollen2021, aichholzer2013,
kenny2001starts; new but uncited by Section 2: kennykashy2006 (for Methods).
grimm2020odd and muller2013oddd are cited only in the ODD appendix (moving to the ESM).

## G. Problems noticed in files owned by others (not edited)

- `sections/introduction.tex` line 19 calls CoDiNG "the CoDiNG preprint"; it is now a peer-reviewed article (IEEE TCSS, early access).
- line 25 cites the preprint `dang2026` first and unlabeled for "power analysis shows…"; Section 2 now cites `mulder2023` first and labels the preprint (domain m10).
- line 36 contains "No single component of this design is new" and the search details (OpenAlex, Semantic Scholar, arXiv, dates); per plan §5 the sentence appears once, in Section 2, and the search record goes to the ESM. It also references `\ref{sec:related}`, which disappears with `related-work.tex` (use `sec:background` or `sec:bg-positioning`).
- line 39 states Manski as "group outcomes alone do not identify endogenous peer effects without information about reference groups"; acceptable but less precise than §D.
- `sections/discussion.tex` line 69 says reinforcement and heterogeneous processes "can generate the same joint outcome distribution, including grouped observations"; the precise statement is existence of both twins for any longitudinal distribution with unrestricted functional forms (§D).
- `sections/methods.tex` line 13 (actor–partner models) cites only `kim2024`; domain m13 asks for Kenny, Kashy and Cook (2006): entry `kennykashy2006` now exists.
- Plan §5 lists "dense network" among the reasons the unobserved-network panel route does not apply. Eight uniform random contacts among about ten thousand respondents is a sparse network; the verified reasons are the linear models of those methods, the need for many periods relative to ties per unit (de Paula et al.) or many small known groups (Lewbel et al.) or many trajectories (Lang et al.), against eleven waves of one realization with a nonlinear influence rule. Section 2 uses these.
- Plan §5 asks for "CoDiNG preprint, labeled preprint"; the work is no longer a preprint (§B).

## Independent verification (13/10/2026)

A second agent, without access to the first agent's conclusions as evidence,
rechecked commit `5cc19119` against `35b7942a`: every added or changed entry's
metadata against Crossref, DataCite, arXiv, OpenReview, NBER, publisher pages or
library catalogs, and every citation of Section 2 against the source (abstract at
least; full text where marked in its report). It found no fabricated reference, no
wrong DOI and no claim credited to the wrong work. Fixes applied afterwards:

- `moor2026`: the minimum-change result concerns the generating model rerun with its
  true parameters; the calibrated model mimics the no-change baseline when the signal
  is weak (arXiv:2602.00876v1, §3.1, pp. 7–8).
- `feller1943`: "An early statement is Feller's", since Feller credits the two
  readings to earlier authors (p. 389).
- `hill2001`: cited together with `hillkriesi2001`, where the term "durable changers"
  appears.
- `lersch2023`: the three-wave limit is stated with the source's qualifiers
  (simulations; a three-wave, four-year panel such as the GSS; pp. 222, 245).
- Positioning table, note f: "Test of the influence parameter against zero in the same
  model" (Stadtfeld et al., Table 4 caption).
- `gourieroux1993`: pages moved to `note` so that the S prefix prints.
- `soni2019rankers`: booktitle names the PMLR volume (2019 ACM SIGKDD Workshop on
  Causal Discovery, PMLR 104).

Sources the second agent could not open and checked through secondary records:
the Springer chapter of `moor2026` (checked through the arXiv version), Cambridge Core
for `hill2001`, and the primary text of `converse1964` ("black-and-white" model checked
through the Political Analysis abstract of Hill and Kriesi).

## Round 4 additions (14/10/2026)

- `gestefeld2023` (new claims in Section 5.4): checked by the coordinator against the
  open JASSS full text (https://www.jasss.org/26/4/9.html) on 14/10/2026. Each step, an
  agent's change depends on "the opinion of a randomly selected agent j"; idiosyncratic
  change makes the agent "change its opinion back to its initial opinion"; the
  Discussion states "The best-fitting time step count is 24" (Table 3: 24.8 and 23.9 for
  the two best microscopic fits, optimized over 1–30 steps per SHP year). Status: verified.
- `sasahara2021` (Section 2.1): metadata and the cited claim checked by the round-4
  writer against the Crossref record and abstract (J. Comput. Soc. Sci. 4, 381–402).
  Status: verified at abstract level.
- `takacs2016` (Section 2.1, "which also speaks against a confidence bound"): the cited
  finding is verified above; the clause is the authors' inference from it (influence
  that grows with opinion distance is not limited by a confidence bound). Status:
  interpretation, marked as such here.
- `hill2001`: corrected to Jennifer L. Hill as sole author of the APSR article (Crossref
  record for 10.1017/S0003055401002209 and the RePEc record list only her); Hill and Kriesi
  are the authors of the companion Political Analysis article (`hillkriesi2001`).

## Round 5 additions (14/10/2026)

# Round 5 literature verification (task L2, 2026-10-13)

Inputs: `round5.md` decision 5; second-panel reports `review-20261014b/panel2-jcss-reviewer-measurement.md`
(m8 and §4 item 5) and `panel2-jcss-reviewer-opinion.md` (m6, §6 item 5); first-round reports in
`review-20261014/` for the original requests. Output: `round5-entries.bib` (6 entries). No repository
file was edited.

## Summary

| Key                                      | Status                                                                                            | What it can be cited for                                                                                                                                     | Basis                                     |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------- |
| `bollencurran2004`                       | verified                                                                                          | ALT models nest the autoregressive (simplex) and latent-trajectory (growth-curve) models: autoregression plus person-specific trajectories                   | publisher abstract                        |
| `asparouhov2018`                         | verified                                                                                          | DSEM: person-specific means and autoregressive parameters, AR(1) with measurement error, ARMA(1,1), time-varying parameters                                  | full text                                 |
| `lipps2007`                              | verified                                                                                          | SHP attrition, waves 2000–2005, higher among people with little political interest (composite includes trust in the federal government) and the dissatisfied | full text                                 |
| `voorpostel2010`                         | verified                                                                                          | SHP I 1999–2008: those who left showed less political interest and less trust in the federal government; the bias is "mild"                                  | full text                                 |
| `saris2014`                              | verified                                                                                          | quality = reliability × validity (coefficients), method effects = 1 − validity²; quasi-simplex treats temporary components as error                          | 2nd-edition text snippets                 |
| `alwinkrosnick1991reliability` (new key) | verified                                                                                          | reliability of 96 attitude items from 3-wave reinterviews; question attributes; older and less-schooled respondents least reliable                           | publisher abstract                        |
| `alwin2007` (existing)                   | metadata correct                                                                                  | facts reported more reliably than nonfacts (attitudes, beliefs, values, self-assessments)                                                                    | book text snippets, publisher description |
| `alwinkrosnick1991` (existing)           | metadata correct, but it is the AJS paper on age and **stability**, not the SMR reliability paper | impressionable-years and aging-stability support for party identification only                                                                               | abstract                                  |
| `tang2025empirical` (existing)           | claim verified; title needs one-word fix                                                          | Model A conclusion reverses when the quadratic-shape effect is dropped (Model C), per the authors                                                            | full text                                 |

Nothing requested was dropped.

## How sources were checked

- Metadata: Crossref works API; DataCite API (Lipps); K10plus SRU (MARC) and zbMATH API for the books;
  Google Books volume pages; Open Library; the published PDFs' running heads.
- Content: open full texts (Utrecht University repository copy of the publisher version of DSEM; the
  published PDFs of Lipps and Voorpostel from the University of Lausanne repository, IRIS/Serval;
  JASSS HTML for Tang). For the two Wiley books: Google Books "search within volume" snippets
  ("Pages displayed by permission of John Wiley & Sons"), the publisher description, and Wiley's own
  excerpt PDFs (contents and index) for Alwin. Abstracts from Crossref (publisher-deposited) or OpenAlex.
- No API call carried an e-mail, `mailto` or contact header (Crossref, OpenAlex, DataCite, Semantic
  Scholar, Europe PMC, PMC OAI, K10plus, zbMATH, Open Library, SUDOC). Unpaywall was not used because
  it requires an e-mail.
- Blocked (HTTP 403 or bot challenge): Wiley Online Library and wiley.com, UChicago Press, Deep Blue
  (Michigan OA copy of the SMR article), the _MDA_ journal site, SSOAR (Anubis), e-bookshelf, Library
  of Congress. The Google Books API had no quota left; the HTML search-within endpoint worked. CiteSeerX
  no longer serves Bollen and Curran. The Chrome extension was not used.
- Fetched pages were treated as data. Quotes are short fragments; page numbers are journal or book pages.
- Rendering: a scratch document with `sn-jnl` (`iicol`), the template `sn-mathphys-num.bst` after the
  build's `bibliography_style()` edit, and tectonic `--only-cached` compiled with **no BibTeX warnings**
  (output at the end). None of the six keys or DOIs exists in the journal `references.bib`.

## A. New entries

### bollencurran2004

- Metadata: Crossref 10.1177/0049124103260222: _Sociological Methods & Research_ 32(3):336–383,
  February 2004. Crossref drops the colon in the title; the Carolina Population Center record
  (cpc.unc.edu/resources/publications/bib/2547) gives "Autoregressive Latent Trajectory (ALT) Models:
  A Synthesis of Two Traditions".
- Read: abstract (Crossref; identical on the CPC page). No open full text was found (the CiteSeerX
  copy is gone; the search found only the SAGE landing page, which was not requested).
- Quotes: "two approaches are of particular historical importance: the autoregressive (simplex) model
  and the latent trajectory (curve) model"; "We argue that the autoregressive and trajectory models are
  special cases of a more encompassing model that we call the autoregressive latent trajectory (ALT)
  model"; in family income data on 3,912 adults over seven years they "find evidence for both
  autoregressive and latent trajectory processes".
- Model form, from a secondary source only (Ou, Chow, Ji and Molenaar 2017, _Multivariate Behavioral
  Research_, PMC8279042; not proposed for citation): "The AR part of the model permits individual i's y
  value at time t − 1 to influence the individual's current y value … This parameter is held invariant
  across individuals, but may be freed to vary over time. The person-specific terms, αi and βi, are
  components of the growth curve portion".
- Claim for the article: persistence that adds person-specific latent trajectories (levels and trends)
  to autoregression between waves is a model family the study did not evaluate.
- Caution: do not present ALT as the source of model B. B has a person-specific level but no
  person-specific slope, and puts the autoregression on a latent state with response error.
- Status: verified (abstract).

### asparouhov2018

- Metadata: Crossref 10.1080/10705511.2017.1406803: _Structural Equation Modeling: A
  Multidisciplinary Journal_ 25(3):359–388, issue 2018, online 27 December 2017. The authors' names
  match the article's first page.
- Read: full text, publisher version deposited at dspace.library.uu.nl/handle/1874/375435.
- Quotes:
  - p. 360: DSEM "combines four different modeling techniques: multilevel modeling, time-series
    modeling, structural equation modeling (SEM), and time-varying effects modeling (TVEM)"; "The most
    general model is the cross-classified DSEM model, which incorporates both individual and
    time-specific random effects".
  - p. 368: random AR(1), Yit = μi + ϕi(Yi,t−1 − μi) + ζit, where "The variables μi and ϕi have a
    bivariate normal distribution". This gives a person-specific mean (a trait) and person-specific
    persistence.
  - p. 371: "measurement error AR(1) model—that is, MEAR(1)—because the latent variable ft follows an
    AR(1) process but is not observed directly; rather, it is measured with error".
  - p. 372: "The AR(1) model has an exponential decay of the autocorrelation function and the
    ARMA(1,1) autocorrelation decays slower"; "there are many other possibilities, such as the AR(2)
    model, the more general ARMA(p,q) model, or a MEAR(p) model".
  - p. 380: "In the models thus far, the parameters were allowed to differ across individuals, but were
    assumed to be stable over time. Here we illustrate the TVEM feature".
- Claim for the article: models with person-specific or time-varying autoregressive parameters, or with
  ARMA(1,1)-type serially correlated innovations, exist in a common framework, and the study evaluated
  none of these extensions.
- Cautions:
  - DSEM is presented for intensive longitudinal data (abstract: "observations from multiple
    individuals are collected at many points in time"). Its simulations use long series; for
    MEAR(1)/ARMA(1,1) with N = 1, "Good estimation … needs at least T ≥ 200" (p. 372). Do not imply
    it is routinely estimable on 11 annual waves.
  - My mapping, not a statement in the source: B with a fixed φ is close to DSEM's two-level MEAR(1)
    with a person-specific mean. The unevaluated part is the extensions listed above.
- Status: verified (full text).

### lipps2007

- Metadata: published PDF, running head "Methoden – Daten – Analysen · 2007, Jg. 1, Heft 1, S. 45-68"
  (English text with a German abstract). The IRIS/Serval record gives volume 1, issue 1, pp. 45–68,
  ISSN 1864-6956. DOI 10.12758/mda.2007.003 is registered at DataCite by GESIS (title "Attrition in the
  Swiss Household Panel", creator Lipps, Oliver; registered 2017). doi.org redirects it to
  mda.gesis.org …/article/view/2007.003, which blocked this client. Voorpostel 2010 cites it as
  "Methoden – Daten – Analysen, 1(1): 45–68". The task brief's guess "Survey Research Methods" is wrong.
- Read: full text.
- Quotes:
  - p. 45, abstract: "attritors are in general the younger people and the males, foreigners, the
    socially and politically “excluded”, i.e. those who show little social and political interest and
    participation, those who are mostly dissatisfied with various aspects in their life"; "This pattern
    is rather cumulative than compensating over panel waves".
  - p. 57: the "political interest" composite combines interest in politics, "in degree to which the
    respondent has trust in the federal government" (sic), self-assessed political influence, and the
    number of ten votes one would take part in. The trust component is the article's SHP item.
  - p. 60: "being interested in politics and potentially participating in political or societal
    activities largely decrease the odds to attrite"; "the lowest attrition can be expected from those
    with a high political interest. This pattern holds virtually during all panel waves".
  - p. 67, Table 2: attrition odds ratios for political interest are .77, .82, .79, .75 and .74 in five
    of six wave-to-wave models (2001 not significant at 1%), and .82 in the all-wave model.
- Sample: first-wave (1999) respondents, waves 2000–2005.
- Claim for the article: in the SHP, attrition was higher among respondents with less political
  interest (a composite that includes trust in the federal government) and among the dissatisfied.
- Status: verified (full text).

### voorpostel2010

- Metadata: published PDF, running head "Swiss Journal of Sociology, 36 (2), 2010, 359–377" (© Seismo
  Verlag), matching the IRIS/Serval record. There is no DOI and no Crossref record. The task brief's
  guess "Survey Research Methods" is wrong. The title is in title case, as in the article heading.
- Read: full text.
- Data: SHP I, 1999–2008. The groups are "always in" (25.5%), "ever out" (27.6%) and "lost" (45.3%)
  (p. 366).
- Quotes:
  - p. 369, Table 1: mean trust in government (0–10) is 6.00 for always in, 5.83 for ever out and 5.65
    for lost (t = 2.98** and 6.66***). Interest in politics is 5.43, 5.07 and 4.71.
  - p. 370: "'Always in' respondents scored higher on participation in clubs, participation in polls,
    general trust in people, political interest, and trust in the federal government compared to the
    two other groups".
  - p. 371, Table 2: in the multinomial model with demographics and social involvement, lost against
    always in gives interest in politics B = −.043*** (Exp(B) .958) and trust in government
    B = −.039** (Exp(B) .962). Neither is significant for ever out.
  - p. 372: "The group of respondents that left the panel further distinguished themselves from those
    who were interviewed in every wave by demonstrating less interest in political matters and less
    trust in the federal government". However, "Those variables related to behaviour rather than those
    reflecting attitudes were important for both" groups, and Nagelkerke R² was .036 and .067.
  - p. 374: "there is a nonresponse bias in the Swiss Household Panel, but it seems mild".
- Claim for the article: same direction as Lipps, for the trust item itself. Respondents who left the
  SHP had reported less trust in the federal government and less political interest.
- Status: verified (full text).

Caution for both SHP papers: they support the **direction** of the X5 trust-dependent attrition and
the fact that such attrition exists in the SHP. They do not calibrate its size. Voorpostel calls the
bias mild and reports a per-point Exp(B) of .962 for a multi-wave outcome. The X5 retention odds
ratios of 1.5 and 2 per unit of the latent state are set by the design, and the ESM already says
"not estimates for the SHP". Keep that wording. Voorpostel also notes (p. 375) that changes in
attitudes over the panel were not modeled.

### saris2014

- Metadata:
  - Crossref 10.1002/9781118634646 (Wiley, 2014; ISBN 9781118634615 print, 9781118634646 online). Its
    back-matter record "WILEY SERIES IN SURVEY METHODOLOGY" is pp. 356–357.
  - Crossref types the book as "edited-book", lists Saris and Gallhofer as editors and gives
    edition-number 1. All three are wrong for this item.
  - K10plus MARC gives 250 "Second edition" / "2nd ed.", 264 "Hoboken, NJ : J. Wiley & Sons, c2014",
    245 $c "Willem E. Saris, and Irmtraud N. Gallhofer", 490 "Wiley series in survey methodology", and
    024 with the DOI.
  - zbMATH (Zbl 1288.62014) gives "2nd updated ed. Wiley Series in Survey Methodology. Hoboken, NJ:
    John Wiley & Sons … (2014)". Google Books gives Edition 2, John Wiley & Sons, 2014.
  - The publisher name is spelled as in the existing `alwin2007`.
- Read: text snippets of the 2nd edition (Google Books id zDOpAgAAQBAJ, search within volume) and the
  publisher description. The full text was not read.
- Quotes (2nd edition pages):
  - p. 179, chapter 9 "Criteria for the Quality of Survey Measures": "total quality of a measure is
    defined as the strength of the relationship between the observed variable and the variable on
    interest, that is, (rv)²" (sic, "on interest").
  - p. 295: "quality coefficient is the product of the reliability and the validity coefficient and the
    quality itself is the quality coefficient squared, which can be interpreted as the percentage
    explained variance in the observed variable by …".
  - p. 296: "method effects because they are the complement of validity (1 - validity coefficient
    squared)".
  - p. 166: "Campbell and Fiske (1959) suggested that validity, reliability, and method effects can be
    evaluated only if more than one method is used to measure the same trait".
  - p. 182, quasi-simplex: "suggested by Heise (1969), improved by Wiley and Wiley (1970), and used by
    Alwin …"; p. 182 continues "Alwin and Krosnick (1991) to …".
  - p. 183: "The second problem is that any temporary component in the variables that is not present at
    the next occasion will be treated as error, while it might be a substantive part of the latent
    variable at a given point in time".
- Claims for the article:
  1. (Requested) Reliability is not quality. Quality is the product of the reliability and validity
     coefficients, squared, and method effects are 1 − validity². Measurement quality is therefore the
     closer concept to what the simulation calls signal share (Online Resource 1 S8.4).
  2. (Optional, fits the N1 rewrite) With one indicator per wave, the quasi-simplex counts a short-lived
     true component as error (p. 183). This is the published form of the measurement referee's
     state–error equivalence.
- Status: verified (book text snippets).

### alwinkrosnick1991reliability (new key)

- Why a new key: the referee asks for "Alwin and Krosnick (1991, _SMR_) 20(1)". The existing
  `alwinkrosnick1991` is a different 1991 article (AJS, see B).
- Metadata: Crossref 10.1177/0049124191020001005: _Sociological Methods & Research_ 20(1):139–181,
  August 1991. Title "The Reliability of Survey Attitude Measurement", subtitle "The Influence of
  Question and Respondent Attributes". Crossref prints the authors' names in capitals; normalized.
- Read: abstract (Crossref, publisher-deposited; OpenAlex identical). The OA full text at Deep Blue
  returned 403.
- Quotes: "reliability is estimated for 96 survey attitude measures using data from five, 3-wave
  national reinterview surveys"; "Attitude questions with more response options tended to have higher
  reliabilities, although there are some important exceptions"; "Older respondents and those with
  less schooling provided the least reliable attitude reports".
- Method corroborated by Saris and Gallhofer 2014, p. 11: "Alwin and Krosnick (1991) followed the
  suggestion by Heise and used the quasi-simplex model to evaluate the quality of survey questions".
- Claim for the article: the reliability of single attitude items, estimated from three-wave panels
  with Heise's model, varies with question format and respondent attributes (lower for older and
  less-schooled respondents).
- Status: verified (abstract).

## B. Existing entries (item 6)

### alwin2007

- Metadata: correct as it stands.
  - Crossref monograph 10.1002/9780470146316: print 2007-06-27, online 2006-12-07, ISBN 9780470081488
    print.
  - K10plus: "Hoboken, N.J : Wiley-Interscience, ©2007", xvi, 389 pp. Wiley-Interscience is a John
    Wiley & Sons imprint.
  - Optional: `series = {Wiley Series in Survey Methodology}` (Crossref back-matter record pp. 391–392)
    for symmetry with `saris2014`.
- Read: text snippets (Google Books id cPFPpGLFcr4C, e-book ISBN 9780470146309); the publisher
  description (Wiley-VCH product page; Penn State Pure abstract); Wiley's excerpt PDFs (contents,
  index).
- Quotes:
  - Publisher description: "research data gathered on nearly 500 survey measures and the application
    of an empirical approach grounded in classical measurement theory".
  - Contents: §5.3 "Estimating Reliability Using the Quasi-Markov Simplex Model" (p. 104); §10.3 "Age
    and Reliability of Measurement" (p. 218).
  - p. 162: "we have confirmed the commonly held view that facts are reported more reliably than are
    nonfacts".
  - p. 171: the nonfactual questions are "beliefs, values, attitudes, self-assessments, and
    self-perceptions".
  - p. 319: "factual survey content is measured with error, although it is perhaps less vulnerable to
    sources of error than are nonfactual questions".
  - p. 230: "if older respondents are differentially affected by method factors, this will tend to
    increase reliability, rather than simply reduce it". This supports "stable response style counts
    as reliable variance", paired with `saris2014`.
- Claim for the article: from panel reliability estimates for nearly 500 survey measures, attitudes and
  other nonfactual reports are measured less reliably than facts.
- Do not cite it for a decline of reliability with age. p. 261: "studies comparing rates of measurement
  error across age groups in actual surveys have generally not been able to demonstrate that aging is a
  major problem in routine use of …".
- Status: verified (book text snippets).

### alwinkrosnick1991

- Metadata: correct and identical to Crossref 10.1086/229744: _American Journal of Sociology_
  97(1):169–195, July 1991, "Aging, Cohorts, and the Stability of Sociopolitical Orientations Over the
  Life Span".
- It is **not** the SMR article on the reliability of attitude measurement. Cite
  `alwinkrosnick1991reliability` for reliability.
- Read: abstract (OpenAlex; the UChicago page blocked this client). Quotes:
  - the hypotheses are "the impressionable-year hypothesis, which states that the youngest adults have
    the least stable attitudes" and "the aging-stability hypothesis, that attitude stability increases
    with age";
  - "When results are aggregated over 50 different measures of attitudes … the youngest adults have
    the lowest levels of attitude stability, although the difference is not significant. Beyond this,
    the aggregated data show very few systematic age-related differences";
  - comparing party identification across the 1956–60 and 1972–76 NES panels "reveals systematic
    differences that provide clear support for the impressionable-years and aging-stability
    hypotheses";
  - "the intensity component of partisan attitudes declines in stability in old age, whereas the
    stability of the direction of party loyalties either increases or persists with age".
- Current uses:
  - `background.tex`: "as when the stability of party identification rises with age". Supported for
    party identification. Do not widen it to attitudes in general.
  - `discussion.tex` limitations: persistence "changing over the life course". Supported.
- Status: verified (abstract).

## C. Tang et al. specification sensitivity (item 7)

- The work meant is `tang2025empirical`, Tang, Snijders and Flache (2025), _JASSS_ 28(1) 2, DOI
  10.18564/jasss.5566.
  - Source of the request: first-round opinion report, §2.5 table ("Their result reverses when the
    quadratic-shape effect is dropped; a clause would be fair") and m6 ("Tang et al.'s finding is
    specification-sensitive"). The second round repeats it (m6, §6 item 5).
- Read: full text, https://www.jasss.org/28/1/2.html.
- Model A, the main model (Table 2; ¶4.1):
  - 1-near similarity (bounded confidence): p.m. 0.0018, p = 0.53, where p is the posterior probability
    that the parameter is positive;
  - 3-far similarity (negative influence): −0.1664, p = 0.03;
  - average similarity, friends: p = 0.95;
  - quadratic shape: −0.2598, p = 0.00. This is a self-correcting tendency of extreme opinions to
    moderate, "unrelated to social influence" (¶4.14).
- Model C, Model A without the quadratic-shape effect (Table 4; ¶4.15): "both the 1-near and 3-far
  similarity effect have a positive parameter estimate in model C, though the estimate for the former
  (p=0.92) is more reliable than that of the latter (p=0.70)".
- The authors' own reading:
  - ¶4.17: "If Model C is presented as the main outcome of the paper, people will come to the conclusion
    that there is evidence of bounded confidence but no evidence of negative influence, completely the
    opposite of our current conclusion from Model A". The same paragraph cautions that empirical studies
    that do not control for this "retracting" mechanism may be affected.
  - They keep Model A because the effect is a "default" SAOM effect, it is significant in Model A, and
    influence effects cannot substitute for it (¶4.16).
  - They state that Model C "does not weaken our previous conclusion" (¶4.15).
- What it supports: the finding (negative influence, little support for bounded confidence) depends on
  modeling a tendency of extreme opinions to moderate. Without that term, the estimates point the other
  way. It is the authors' check, and they keep the main result.
- Suggested clause, after the existing sentence: "…, a conclusion that the authors show reverses when
  a tendency of extreme opinions to moderate is left out of the model \cite{tang2025empirical}".
- Metadata fix for the existing entry (not edited): the version-of-record title ends "…Using Stochastic
  Actor-Oriented **Modelling**". The JASSS page `<title>`, H1, `DC.Title` and `citation_title` all agree;
  only the Crossref deposit says "…Model". Everything else is correct.

## D. Considered, not added

- Secondary sources used only as corroboration; do not cite unless verified separately:
  - Ou, Chow, Ji and Molenaar 2017 (ALT model form);
  - Voorpostel and Lipps 2011, _Journal of Official Statistics_ (change associated with drop-out);
  - Rothenbühler and Voorpostel 2016, Springer chapter (SHP attrition of vulnerable groups).
- Not rechecked here: `lenti2024` and `borile2026`, which were verified at abstract level on
  2026-10-13 in `literature-verification.md`.

## Rendered output (scratch compile, sn-mathphys-num)

```
Bollen, K.A., Curran, P.J.: Autoregressive latent trajectory (ALT) models: A synthesis of two
  traditions. Sociological Methods & Research 32(3), 336–383 (2004) https://doi.org/10.1177/0049124103260222
Asparouhov, T., Hamaker, E.L., Muthén, B.: Dynamic structural equation models. Structural Equation
  Modeling: A Multidisciplinary Journal 25(3), 359–388 (2018) https://doi.org/10.1080/10705511.2017.1406803
Lipps, O.: Attrition in the Swiss Household Panel. Methoden – Daten – Analysen 1(1), 45–68 (2007)
  https://doi.org/10.12758/mda.2007.003
Voorpostel, M.: Attrition patterns in the Swiss Household Panel by demographic characteristics and
  social involvement. Swiss Journal of Sociology 36(2), 359–377 (2010)
Saris, W.E., Gallhofer, I.N.: Design, Evaluation, and Analysis of Questionnaires for Survey Research,
  2nd edn. Wiley Series in Survey Methodology. John Wiley and Sons, Hoboken, NJ (2014).
  https://doi.org/10.1002/9781118634646
Alwin, D.F., Krosnick, J.A.: The reliability of survey attitude measurement: The influence of question
  and respondent attributes. Sociological Methods & Research 20(1), 139–181 (1991)
  https://doi.org/10.1177/0049124191020001005
```

# Coordinator addition, round 5 (2026-10-14)

### hosmer2013 (new key; editor's second-panel item N6)

- Use: Methods, the sentence that an AUC of 0.70 "is often read as the lower end of
  acceptable discrimination". It is cited without a page.
- Metadata: Crossref 10.1002/9781118548387. The record is typed as a monograph, *Applied
  Logistic Regression*, by David W. Hosmer, Stanley Lemeshow and Rodney X. Sturdivant (Wiley,
  2013; ISBN 9780470582473 and 9781118548387). Crossref gives `edition-number` 1, but this is
  the third edition. The Google Books record (id `64JYAwAAQBAJ`) names the same three
  authors and ISBN.
- Claim: two independent secondary sources attribute the guideline to this edition,
  Section 5.2.4, p. 177. They give the bands as 0.5 to <0.7 poor, 0.7 to <0.8 acceptable,
  0.8 to <0.9 excellent, and ≥0.9 outstanding.
  - 2019 JSM Proceedings paper (ww2.amstat.org/meetings/proceedings/2019/data/assets/pdf/1199666.pdf):
    "Hosmer et al. (2013) (p.177) give the following general guidelines", which include
    "0.7 ≤ area under ROC < 0.8 =⇒ acceptable classification".
  - University of Vermont blog post (blog.uvm.edu/tbplante/?p=1024): "0.7 to <0.8:
    Acceptable discrimination", "You'll see the above labels on page 177".
- Not seen: the book page itself. The Google Books preview returned no snippet to this
  client, which is why the article does not print a page.

## Citation-audit corrections (16/10/2026)

- `hill2001`: Kriesi restored as second author, superseding the round 4 entry above.
  Crossref and RePEc list only Hill, but the companion Political Analysis abstract
  (`hillkriesi2001`) calls this article "Hill and Kriesi (2001)" twice, Kriesi's
  publication list includes it, and APSR 95(4) (December 2001) lists an erratum to it
  (JSTOR 3117712; not read). Running text: "Hill and Kriesi".
- `kiley2020`, `sasahara2021`: published corrections added as notes (ASR 87(2):373–381,
  2022; JCSS 5(2):1779, 2022). No number the article quotes from either work is affected.
- `cohencole2008`, `gelastopoulos2025`, `takacs2016`: article numbers now in `note`;
  `gourieroux1993`: pages S85–S118 in `note`; `granger1976`: series name;
  `mcpherson2001`, `sasahara2021`: issue 1; `coding2024`: early access.
- Claims narrowed to the sources: `lopezpaz2017`, `kim2021classifier`, `kiley2020`
  (table: response error "Partly"), `coding2024` (table: event content simulated),
  `gestefeld2023` (size only; refreshment design cited to `voorpostel2025shp`, in Methods
  and in the ODD), `antoun2026` (wordings and countries, not modes), `kennykashy2006`
  (now only for actor–partner models; the measured co-resident pairs are cited to
  `voorpostel2025shp`). Positioning-table notes re-lettered a–k; the note f cited above
  is now h.
