# Environment Architecture

Genestack is making use of some homegrown solutions, community operators, and OpenStack-Helm. Everything
in Genestack comes together to form cloud in a new and exciting way; all built with opensource solutions
to manage cloud infrastructure in the way you need it.

They say a picture is worth 1000 words, so here's a picture.

``` mermaid
---
config:
  theme: neutral
  markdownAutoWrap: false
  themeVariables:
    fontFamily: Nunito
    fontSize: 16px
  flowchart:
    curve: basis
    #rankSpacing: 50
    #nodeSpacing: 80
---

flowchart TB

    subgraph GENESTACK[ "" ]
        direction TB
        subgraph HEADER[ "" ]
            direction TB
            ICON("<img src='/assets/images/logo.svg'; width='200'; max-width: '100%'; />")
            TITLE( Genestack )
        end
        subgraph ROW1[ "" ]
            direction TB
            subgraph ITEM11[ "" ]
                direction RL
                ITEM11ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM11LABEL[ <font color=#e03132>Forecast ]
            end
            subgraph ITEM12[ "" ]
                direction RL
                ITEM12ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM12LABEL[ <font color=#e03132>Learning ]
            end
            subgraph ITEM13[ "" ]
                direction RL
                ITEM13ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM13LABEL[ <font color=#e03132>Customization ]
            end
            subgraph ITEM14[ "" ]
                direction RL
                ITEM14ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM14LABEL[ <font color=#e03132>Support ]
            end                        
        end
        subgraph ROW2[ "" ]
            direction TB
            subgraph ITEM21[ "" ]
                direction RL
                ITEM21ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM21LABEL[ <font color=#e03132>Firewall ]
            end
            subgraph ITEM22[ "" ]
                direction RL
                ITEM22ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM22LABEL[ <font color=#e03132>Security ]
            end
            subgraph ITEM23[ "" ]
                direction RL
                ITEM23ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM23LABEL[ <font color=#e03132>RBAC ]
            end
            subgraph ITEM24[ "" ]
                direction RL
                ITEM24ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM24LABEL[ <font color=#e03132>Artifact ]
            end                        
        end
        subgraph ROW3[ "" ]
            direction TB
            subgraph ITEM31[ "" ]
                direction RL
                ITEM31ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM31LABEL[ <font color=#e03132>Alerting ]
            end
            subgraph ITEM32[ "" ]
                direction RL
                ITEM32ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM32LABEL[ <font color=#e03132>Dashboard ]
            end
            subgraph ITEM33[ "" ]
                direction RL
                ITEM33ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM33LABEL[ <font color=#e03132>Logs ]
            end
            subgraph ITEM34[ "" ]
                direction RL
                ITEM34ICON("<img src='/assets/images/rackspace.svg'; width='80' />")
                ITEM34LABEL[ <font color=#e03132>Automation ]
            end                        
        end
        HEADER ~~~ ROW1                
        ROW1 ~~~ ROW2
        ROW2 ~~~ ROW3
    end

%% Genestack CSS Class Assignments

class GENESTACK group
class HEADER heading
class ICON titleicon
class TITLE caption
class ROW1,ROW2,ROW3 rowstyle
class ITEM11,ITEM12,ITEM13,ITEM14 item
class ITEM11ICON,ITEM12ICON,ITEM13ICON,ITEM14ICON itemicon
class ITEM11LABEL,ITEM12LABEL,ITEM13LABEL,ITEM14LABEL itemlabel
class ITEM21,ITEM22,ITEM23,ITEM24 item
class ITEM21ICON,ITEM22ICON,ITEM23ICON,ITEM24ICON itemicon
class ITEM21LABEL,ITEM22LABEL,ITEM23LABEL,ITEM24LABEL itemlabel
class ITEM31,ITEM32,ITEM33,ITEM34 item
class ITEM31ICON,ITEM32ICON,ITEM33ICON,ITEM34ICON itemicon
class ITEM31LABEL,ITEM32LABEL,ITEM33LABEL,ITEM34LABEL itemlabel

%% Genestack CSS Class Definitions

classDef group      fill: #ced4db,stroke: #e03132,rx: 15, ry: 15
classDef heading    fill: #eaecef,stroke: #e03132,color: #000000,rx: 15, ry: 15
classDef titleicon  fill: none,stroke: #666
classDef caption    fill: none,stroke: #666,font-size: 80px
classDef rowstyle   fill: none,stroke: #666
classDef item       fill: none,stroke: #666,width: 300px
classDef itemicon   fill: none,stroke: #666,width: 100px
classDef itemlabel  fill: none,stroke: #666,color: #e03132,font-size: 26px

```

The idea behind Genestack is simple, build an Open Infrastructure system that unites Public and Private
clouds with a platform that is simple enough for the hobbyist yet capable of exceeding the needs of the
enterprise.
