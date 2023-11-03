# EGLE-Contamination-Analysis
**Executive Purpose:** 
Identifying and Prioritizing Contaminant Cleanup in Michigan by cross-comparing Public Health Factors

**Attribution and Copyright:**
This work is the property of Envirolytica LLC, and produced with the intent to support not-for-profit individuals and organizations. For-profit use requires written permission, in the form of electronic mail, along with a contract detailing approved usage and payment. <u>There is no licensing fee for use by nonprofit and/or governmental organizations.</u> Attribution is required for all uses. For questions, new projects, or donations, see below: 
MJones@Envirolytica.com
www.Envirolytica.com
[Donations:](paypal.me/Envirolytica)

**Background:**
There are thousands of contamination sites across the state of Michigan, as defined by Parts 201 and Parts 213 of the Natural Resources and Environmental Protection Act (NREPA). With limited budget available, determining which contaminanted sites to prioritize for restoration  is a key challenge for regulatory authorities. This project sought to determine a data-driven method to prioritize contaminant sites relative to each district managed by Michigan's environmental agency (EGLE).

**Data Sources:**
Well, Healthcare, Contamination Site, environmental justice, and School data are provided by the state of Michigan through opendata.arcgis.com. Environmental data is managed in the RIDE database, and additional contaminant site locations were supplied via multiple FOIA requests made to EGLE throughout 2022. Direct links to each available source will be provided in the appendix of this file. 

**Data Cleaning:**
Wells are only considered if: 
* The construction data was prior to 50 years from the current date
* The Well depth is greater than 80 feet
* The Well is either used for irrigation, type 1 public use, type 2 public use, type 3 public use, or household use as denoted by the "WELL_TYPE" attribute
* The Well status is either active,unknown, or other as denoted by the "WELL_STATUS" attribute.

Contaminant sites are excluded if: 
* Latitude and longitude coordinates are not explicitely provided.
* The release status is closed as denoted by the "Release Status" attribute

Schools and Hospitals were excluded if they were no longer considered in use. 

**Methodology**
Total Risk: 
  Total Risk Assessed to the Public is based on the following factors: 
  1. The proximity of the contaminated site relative to nearby schools, healthcare facilities, wellhead protection areas, and wells.
  2. The density of schools, healthcare facilities, wellhead protection areas, and wells in a square mile radius.
  3. The chemical(s) present at the contaminated site
  4. The environmental justice score for the surrounding area (as determined by EGLE)
  5.  The assessed urgency of cleanup as termined by EGLE or its designated representatives.

Chemical Risk: 
  Chemicals information was only provided for ~25% of the 50,000+ contaminated sites. As such business type classifications were used to determine what the 2 most common contaminants were for each business type. Then an assumed contaminant was used for each facility where informaton was not specified. 
  
  Chemical risk was weighted with Group i / (i) methodology such that the most conscerning group held a weight six times more important than the least concerning group, and was evaluated based on the chemical type, which was prioritized based on whether the chemical was contained in the following groups: 
  * Chlorinated VOCs and Pesticides (Most Concerning)
  * PFAS, PBB, PCB
  * Petroleum and Hydrocarbon compounds
  * Metals including Lead, Mercury, as well as Aromatic hydrocarbons like Dioxin and PAHs
  * Other chemicals including Methane or items that create concern for Water Quality, PH, or not classified by existing methods.
  * Unknown/Not Listed

District Evaluations: 
  Subsections were taken to than rank each contaminated site by the severity for each district as well to enable District EGLE employees to priority their contaminant sites appropriately. 

Proximity Calculations: 
  The haversine formula was used to calculate the proximity of different sites to neighboring wells, schools and the like. 

**Contact:**
For questions or concerns, please contact Matt Jones: [Email](MJones@Envirolytica.com). 
This project is the culmination of hundreds of hours of work to benefit EGLE Staff. Please consider a donation to support this and future projects. **[Donate here:](paypal.me/Envirolytica)**
