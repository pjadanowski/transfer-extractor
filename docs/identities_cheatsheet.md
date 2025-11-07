 # Insurance Company Aliases

This document contains a list of insurance company identifiers used in the transfer system.

| Company Name | Alias |
|--------------|-------|
| Adam Riese | `adamRiese` |
| Agencio | `agencio` |
| AIG | `aig` |
| Alte Leipziger | `al` |
| Allianz | `alz` |
| AML | `aml` |
| AND Safe | `andSafe` |
| ARAG | `arag` |
| Auxilia | `auxi` |
| AXA | `axa` |
| Basler | `basler` |
| Versicherungskammer Bayern | `bayern` |
| BB | `bb` |
| BM | `bm` |
| CL | `cl` |
| Conceptif | `conceptif` |
| Concordia | `concordia` |
| Conti | `conti` |
| DB | `db` |
| Deurag | `deurag` |
| Dialog | `dia` |
| DMB | `dmb` |
| Docura | `docura` |
| Domcura | `domcura` |
| ERGO | `ergo` |
| Fondsfinanz | `fondsfinanz` |
| Generali (Dialog Sach) | `generali` |
| GEV | `gev` |
| GOT | `got` |
| GVO | `gvo` |
| Hannoversche | `hannoversche` |
| Bayerische Hausbesitzer | `bhvg` |
| Hanse Merkur | `hanseMerkur` |
| HDI | `hdi` |
| HEL | `hel` |
| HFK1676 | `hfk` |
| HKD | `hkd` |
| Ideal | `ideal` |
| Inter | `inter` |
| Interlloyd | `interlloyd` |
| Interrisk | `interrisk` |
| Itzehoer | `iz` |
| Jan | `jan` |
| KM | `km` |
| LV | `lv` |
| Mannheimer | `mannheimer` |
| Manufaktur Augsburg | `manufakturAugsburg` |
| Muenchener | `muenchener` |
| Neo Digital | `neodigital` |
| Nepa | `nepa` |
| NUB | `nub` |
| NV | `nv` |
| OA | `oa` |
| Rhion | `rhion` |
| Roland | `roland` |
| R+V | `ruv` |
| Sachpool | `sachpool` |
| SG | `sg` |
| Standard Life | `stdlife` |
| Swiss | `swiss` |
| VHV | `vhv` |
| VWB | `vwb` |
| Waldenburger | `wald` |
| Wuerttembergische | `wuerttembergische` |
| WWK | `wwk` |
| Zurich | `zurich` |
| Covomo | `covomo` |
| Universa | `universa` |
| Signal Iduna | `signalIduna` |
| VPV | `vpv` |

## Usage

Use these aliases with the `--alias` parameter when running the transfer extractor:

```bash
python main.py --alias zurich --identity "your-identity-string"
python main.py --alias alz --identity "your-identity-string"
python main.py --alias axa --identity "your-identity-string"
```