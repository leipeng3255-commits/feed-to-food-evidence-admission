# Locked local-data reporting extension: milk and eggs

Date: 13 October 2026. This is a post-pilot exploratory extension. It is not preregistered, blinded, a prospective validation study, or a change to the original admission decisions.

## Target and selection before the new result scan

Question: do the previously fixed marginal reporting rules preserve or weaken declared calculations in additional animal-food matrices, and which records prevent a finite full-denominator mean enclosure?

The local official-source manifest is the sampling frame for files, not a population sampling frame. Inspect metadata/sample tables for every existing USDA PDP archive from 2011 through 2024. Use the dictionaries' exact commodity labels Milk (MK) and Eggs (EG). Metadata inspection identified milk/eggs in 2011, 2016 and 2017; the other years remain in the availability audit. PB (Peanut Butter), PK (Pumpkin) and CF (Cauliflower) are not animal foods. Do not select chemicals by their detection results. This scope is milk/eggs, not a complete animal-food ontology or an audit of every database on the disk.

Read all records for those commodities in the admitted source years. Keep the full commodity–analyte universe, including all-marginal cells. Record programme table totals, sample counts, units, result states and commodity-type composition. Verify each file against its existing manifest SHA256 and its ZIP CRC. Keep source years, commodities and analytes separate; do not pool population concentrations or treat adjacent years as independent biological validation studies.

## Fixed transformations and numerical semantics

Use the 8 October bin edges 0,1,10,100,1000,infinity ppb and illustrative strict thresholds 2,10,20 ppb, without tuning. Unit factors from each year's dictionary are B=1, M=1000, T=0.001 to ppb. Both the value and its LOD use the recorded CONUNIT. These conversions do not harmonise toxicological residue definitions or establish laboratory equivalence.

ND requires a blank text-file concentration and positive finite LOD and represents [0,LOD], conditional on the source's validated-well-recovered label. O and R are reported detection point intervals and omit measurement error. NP is marginal-performing ND, not ordinary ND. Unsupported states, invalid values/units/limits, or contradictions remain unknown; none is zero-filled or imputed. Retain NP and invalid records in full-denominator [0,infinity] sensitivity. No finite cap is fitted or preferred.

R0 retains detections and ND limits; R1 bins only detection values while retaining ND limits; R2 retains status/denominator information but no numerical magnitudes or limits and represents [0,infinity]. Recompute each representation solely from its retained interval histogram. Require direct-sum agreement, identical working denominators, and enclosure nesting. No inferential sampling interval, toxicity threshold, dose model, risk trend or attribution fraction is estimated.

Primary unit: year×commodity×analyte cell, on the archive's reported concentration basis. Sample identifiers only establish record keys, not farm/biological independence. Repeated sample–analyte keys hold that cell for investigation rather than being silently deduplicated or averaged. Descriptive commodity-type counts are retained; no assertion of processed-food or risk-definition compatibility follows from the commodity code.

## Outputs and interpretation

Deliver the complete metadata eligibility table, source receipts, cell results, retained histograms, per-stratum summary, and a reporting-statistic table (n, endpoint sums and strict-threshold endpoint counts). A separate standard-library checker must verify the bundle hashes and reconstruct declared endpoints without raw files/configuration.

Report unchanged and widened working-cell intervals, full-denominator unknown cells, and target-specific threshold ambiguity, without comparison of national safety or framework accuracy. Dairy/egg results may broaden the descriptive reporting example but cannot repair the missing feed–ration–transfer–consumption chain. Keep original 2009/2010 results and parent/plant analyses unchanged.

Pre-existing GIFT/FCID/INCA3 and cohort databases are audit candidates, not automatic exposure inputs. Required food-form, population/time, measurement/residue-definition and processing decisions must be documented before joining them to monitoring. No individual consumption records are exported in this extension.
