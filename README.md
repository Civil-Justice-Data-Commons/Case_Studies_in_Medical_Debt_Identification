# Case Studies in Medical Debt Identification

This repository contains Python code for case studies in methods for medical debt identification in court records, which are evaluated in the Civil Justice Data Commons Report *The Challenges of Identifying Medical Debt in Court Records*. 

The medical debt identification methods included in this code are:
- **Physician Consultation Method** *A novel method developed for this case study.*
- **Machine Learning Generated Terms Method**
- **Manual Review of Top Cases Method**
- **CMS Facility Names Method**

Each medical debt identification method were used to generate a set of substrings, which were then used with simple string matching and fuzzy string matching (using Levenshtein Distance).

This case study was run on the Civil Justice Data Commons instance on the Redivis platform. Code specifically interfacing with this cloud computing platform is signaled by comments, and may need to be replaced with equivalent calls when porting the code for running on another platform. 

The implementation of these methods was written by James Carey, a Policy Fellow at Georgetown's Massive Data Institute working on the Civil Justice Data Commons Project. This implementation and the development of the Physician Consultation Method were aided by Dr. Fatu S. Conteh, Jordan Rinaldi, Stephanie Straus, a Policy Fellow at Georgetown's Massive Data Institute, and Margaret Haughney, a Policy Analyst at Georgetown's Massive Data Institute.
