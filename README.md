# EGLE-Contamination-Analysis
Identifying and Prioritizing Contaminant Cleanup in Michigan by cross-comparing Public Health Factors

Attribution and Copyright: This work is the property of Envirolytica LLC, and produced with the intent to support not-for-profit individuals and organizations. For-profit use requires written permission, in the form of electronic mail, along with a contract detailing approved usage and payment. Not-for-profit use is freely available. 

Background: 
There are thousands of contamination sites across the state of Michigan, as defined by Parts 201 and Parts 213 of the Natural Resources and Environmental Protection Act (NREPA). With limited budget available, determining which contaminanted sites to prioritize for restoration  is a key challenge for regulatory authorities. This project sought to determine a data-driven method to prioritize contaminant sites relative to each district managed by Michigan's environmental agency (EGLE).

Data Sources: 
Well, Healthcare, Contamination Site, environmental justice, and School data are provided by the state of Michigan through opendata.arcgis.com. Environmental data is managed in the RIDE database, and additional contaminant site locations were supplied via multiple FOIA requests made to EGLE throughout 2022. Direct links to each available source will be provided in the appendix of this file. 

Data Cleaning: 
Wells are only considered if: 
* The construction data was prior to 50 years from the current date
* The Well depth is greater than 80 feet
* The Well is either used for irrigation, type 1 public use, type 2 public use, type 3 public use, or household use as denoted by the "WELL_TYPE" attribute
* The Well status is either active,unknown, or other as denoted by the "WELL_STATUS" attribute.

Contaminant sites are excluded if: 
* Latitude and longitude coordinates are not explicitely provided.
* The release status is closed as denoted by the "Release Status" attribute
