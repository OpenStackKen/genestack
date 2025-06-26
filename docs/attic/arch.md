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

    subgraph TW [ <font size=6em color=white>Tenant Workloads ]
        direction TB
        subgraph WLWRAP [ "" ]
            direction TB
            subgraph CW [ "" ]
                subgraph CWTITLE [ Containerized Workloads ]
                    direction TB
                    C1{ "" }@{ img: "/assets/images/container.svg", w: 160, h: 80 }
                    C2{ "" }@{ img: "/assets/images/container.svg", w: 160, h: 80 }
                    C3{ "" }@{ img: "/assets/images/container.svg", w: 160, h: 80 }
                    C4{ "" }@{ img: "/assets/images/container.svg", w: 160, h: 80 }
                end
            end
            subgraph VW [ "" ]
                subgraph VWTITLE [ Virtualized Workloads ]
                    direction TB
                    VM1( "" )@{ img: "/assets/images/server.svg", w: 160, h: 80 }
                    VM2( "" )@{ img: "/assets/images/server.svg", w: 160, h: 80 }
                    VM3( "" )@{ img: "/assets/images/server.svg", w: 160, h: 80 }
                    VM4( "" )@{ img: "/assets/images/server.svg", w: 160, h: 80 }
                end
            end
        end
    end

    CNI( Container Network Interface )
    OP( Operators )

    subgraph SERVICES[ "" ]
        direction TB
        subgraph SVC1[ "" ]
            direction LR
            subgraph STACK1[ "" ]
                direction TB
                S1("<img src='/assets/images/openstack.svg'; width='80' />")
                S1LABEL[ OpenStack Compute Hosts ]
            end
            subgraph KUBE1[ "" ]
                direction TB
                K1("<img src='/assets/images/kubernetes.svg'; width='80' />")
                K1LABEL[ Worker Host ]
            end
            STACK1[ OpenStack Compute Hosts ]
        end
        subgraph SVC2[ "" ]
            direction LR
            subgraph STACK2[ "" ]
                direction TB
                S2("<img src='/assets/images/openstack.svg'; width='80' />")
                S2LABEL[ OpenStack Infrastructure Hosts ]
            end
            subgraph KUBE2[ "" ]
                direction TB
                K2("<img src='/assets/images/kubernetes.svg'; width='80' />")
                K2LABEL[ Worker Host ]
            end
            STACK2[ OpenStack Infrastructure Hosts ]
        end
        subgraph SVC3[ "" ]
            direction LR
            subgraph STACK3[ "" ]
                direction TB
                S3("<img src='/assets/images/rackspace.svg'; width='80' />")
                S3LABEL[ Rackspace Managed Services ]
            end
            subgraph KUBE3[ "" ]
                direction TB
                K3("<img src='/assets/images/kubernetes.svg'; width='80' />")
                K3LABEL[ Controller Host ]
            end
        end
    end

    subgraph OS[ "" ]
        direction TB
        subgraph OSR[ "" ]
            ROS[ "" ]
        end
        subgraph OSCONTENT[ "" ]
            direction TB
            OSICON("<img src='/assets/images/linux.svg'; width='60' />")
            OSTITLE[ Operating System ]
        end
        subgraph OSL[ "" ]
            SOL[ "" ]
        end
    end

    subgraph HW[ "" ]
        direction TB
        subgraph HWR[ "" ]
            ROOF[ "" ]
        end
        subgraph HWCONTENT[ "" ]
            direction TB
            HWICON("<img src='/assets/images/hardware.svg'; width='60' />")
            HWTITLE[ Physical Hardware ]
        end
        subgraph HWL[ "" ]
            FOOL[ "" ]
        end
    end
    TW ~~~ CNI
    CNI ~~~ OP
    OP ~~~ SERVICES
    SERVICES ~~~ OS
    OS ~~~ HW

%% RefArch CSS Class Assignments

class TW tw
class WLWRAP wlwrapper

class SPACER0 spacer

class VW,CW wl
class CWTITLE,VWTITLE wltitles
class C1,C2,C3,C4 container
class VM1,VM2,VM3,VM4 vm

class CNI cni
class OP operators

class SERVICES services
class SVC1,SVC2,SVC3 svc
class KUBE1,KUBE2,KUBE3 k8s
class K1LABEL,K2LABEL,K3LABEL k8slabel
class K1,K2,K3 k8sicon
class STACK1,STACK2,STACK3 stack
class S1LABEL,S2LABEL,S3LABEL stacklabel
class S1,S2,S3 stackicon

class OSICON osicon
class OSTITLE oscaption
class OSL,OSR spacer
class SOL,ROS blank
class OSCONTENT oscontent
class OS os

class HWICON hwicon
class HWTITLE hwcaption
class HWL,HWR spacer
class FOOL,ROOF blank
class HWCONTENT hwcontent
class HW hardware

%% RefArch CSS Class Definitions
    classDef tw             fill: #858e96,stroke: #383a3c,stroke-width: 2px,rx: 15,ry: 15,height: 350px
    classDef wlwrapper      fill: none,stroke: none,color: none,height: 1px
    classDef wl             fill: #ffffff,stroke: #383a3c,color: #383a3c,rx: 15,ry: 15,font-size: 24px,width: 950px,height: 200px,y: 30px
    classDef wltitles       fill: none,stroke: none,font-size: 24px,color: #383a3c
    classDef container      fill: none,stroke: none
    classDef vm             fill: none,stroke: none
    classDef cni            fill: #a4d8ff,stroke: #1971c2,stroke-width: 4px,stroke-dasharray: 4 4,rx: 15,ry: 15,padding: 2100px,font-size: 32px,height: 80px,text-align:center,y: -40px,width: 2100px,x: -1050px
    classDef operators      fill: #b1f2bc,stroke: #2f9e44,stroke-width: 4px,stroke-dasharray: 4 4,rx: 15,ry: 15padding: 2100px,font-size: 32px,height: 80px,text-align:center,y: -40px,width: 2100px,x: -1050px
    classDef services       fill: none,stroke: none,height: 10
    classDef svc            fill: #e8ecef,stroke: #5193d1,stroke-width: 2px,rx: 15,ry: 15,height: 300px,y: 50px
    classDef k8s            fill: none,stroke: none,color: #383a3c,height: 1px,y: 155px
    classDef k8sicon        fill: none,stroke: none,color: #383a3c,height: 1px
    classDef k8slabel       fill: none,stroke: none,color: #383a3c,font-size: 24px
    classDef stack          fill: #fff,stroke: #e26061,stroke-width: 2px,color: #383a3c,rx: 15,ry: 15,height: 120px,y: 15px
    classDef stackicon      fill: none,stroke: none,color: #383a3c,height: 10px
    classDef stacklabel     fill: none,stroke: none,color: #383a3c,font-size: 24px,padding: 280px,height: 1px
    classDef spacer         fill: none,stroke: none,color: none,justify-content: center,width: 675px,height: 1px
    classDef blank          fill: none,stroke: none,color: none,width: 475px,height: 1px
    classDef osicon         fill: none,stroke: none,color: none,height: 1px
    classDef oscaption      fill: none,stroke: none,font-size: 32px,height: 1px
    classDef oscontent      fill: none,stroke: none,color: none,height: 1px
    classDef os             fill: #ffec99,stroke: #f08c01,stroke-width: 4px,stroke-dasharray: 4 4,color: #383a3c,rx: 15,ry: 15,height: 150px,y: 20
    classDef hwicon         fill: none,stroke: none,color: none,height: 1px
    classDef hwcaption      fill: none,stroke: none,font-size: 32px,height: 1px
    classDef hwcontent      fill: none,stroke: none,color: none,height: 1px
    classDef hardware       fill: #ffffff,stroke: #1e1e1e,color: #1e1e1e,stroke-width: 2px,rx: 15,ry: 15,height: 150px,y: 20


```

The idea behind Genestack is simple, build an Open Infrastructure system that unites Public and Private
clouds with a platform that is simple enough for the hobbyist yet capable of exceeding the needs of the
enterprise.
