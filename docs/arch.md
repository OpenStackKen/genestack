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
    fontFamily: Inter
    fontSize: 16px
  flowchart:
    subGraphTitleMargin: 10
    curve: bumpX
    #rankSpacing: 50
    #nodeSpacing: 80
---

flowchart TB
    subgraph TW [ "" ]
        direction TB

        subgraph TWTITLE [ Tenant Workloads ]
            direction TB
            subgraph CW [ "" ]
                subgraph CWTITLE [ Containerized Workloads ]
                    direction TB
                    C1{ "" }@{ img: "http://localhost:8080/container.svg", w: 120, h: 60 }
                    C2{ "" }@{ img: "http://localhost:8080/container.svg", w: 120, h: 60 }
                    C3{ "" }@{ img: "http://localhost:8080/container.svg", w: 120, h: 60 }
                    C4{ "" }@{ img: "http://localhost:8080/container.svg", w: 120, h: 60 }
                    C5{ "" }@{ img: "http://localhost:8080/container.svg", w: 120, h: 60 }
                end
            end
            subgraph VW [ "" ]
                subgraph VWTITLE [ Virtualized Workloads ]
                    direction TB
                    VM1( "" )@{ img: "http://localhost:8080/server.svg", w: 120, h: 60 }
                    VM2( "" )@{ img: "http://localhost:8080/server.svg", w: 120, h: 60 }
                    VM3( "" )@{ img: "http://localhost:8080/server.svg", w: 120, h: 60 }
                    VM4( "" )@{ img: "http://localhost:8080/server.svg", w: 120, h: 60 }
                    VM5( "" )@{ img: "http://localhost:8080/server.svg", w: 120, h: 60 }
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
                S1@{ img: "https://raw.githubusercontent.com/OpenStackKen/vendor-icons-svg/refs/heads/main/openstack.svg", w: 60, h: 60, contraint: "on" }
                S1LABEL[ OpenStack Compute Hosts ]
            end
            subgraph KUBE1[ "" ]
                direction TB
                K1@{ img: "https://raw.githubusercontent.com/OpenStackKen/vendor-icons-svg/refs/heads/main/kubernetes.svg", w: 60, h: 60, constraint: "on" }
                K1LABEL[ Worker Host ]
            end
            STACK1[ OpenStack Compute Hosts ]
        end
        subgraph SVC2[ "" ]
            direction LR
            subgraph STACK2[ "" ]
                direction TB
                S2@{ img: "https://raw.githubusercontent.com/OpenStackKen/vendor-icons-svg/refs/heads/main/openstack.svg", w: 60, h: 60, contraint: "on" }
                S2LABEL[ OpenStack Infrastructure Hosts ]
            end
            subgraph KUBE2[ "" ]
                direction TB
                K2@{ img: "https://raw.githubusercontent.com/OpenStackKen/vendor-icons-svg/refs/heads/main/kubernetes.svg", w: 60, h: 60, constraint: "on" }
                K2LABEL[ Worker Host ]
            end
            STACK2[ OpenStack Infrastructure Hosts ]
        end
        subgraph SVC3[ "" ]
            direction LR
            subgraph STACK3[ "" ]
                direction TB
                S3@{ img: "https://raw.githubusercontent.com/OpenStackKen/vendor-icons-svg/refs/heads/main/rackspace.svg", w: 60, h: 60, contraint: "on" }
                S3LABEL[ Rackspace Managed Services ]
            end
            subgraph KUBE3[ "" ]
                direction TB
                K3@{ img: "https://raw.githubusercontent.com/OpenStackKen/vendor-icons-svg/refs/heads/main/kubernetes.svg", w: 60, h: 60, constraint: "on" }
                K3LABEL[ Controller Host ]
            end
        end
    end
    OS( Operating System )
    HW( Physical Hardware )

TW ~~~ CNI
CNI ~~~ OP
OP ~~~ SERVICES
SERVICES ~~~ OS
OS ~~~ HW

class TW tw
class TWTITLE twtitles
class SPACER0 spacer
class VW,CW wl
class CWTITLE,VWTITLE wltitles
class C1,C2,C3,C4,C5 container
class VM1,VM2,VM3,VM4,VM5 vm
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
class OS os
class HW hardware

%% Display Classes
    classDef tw             fill: #858e96,stroke: #383a3c,stroke-width: 2px,rx: 15,ry: 15,height: 400px,y: -10px
    classDef twtitles       fill: none,stroke: none,font-size: 24px,color: #ffffff,font-style: bold
    classDef wl             fill: #fff,stroke: #383a3c,color: #383a3c,rx: 15,ry: 15,font-size: 24px,height: 200px,width: 1000px
    classDef wltitles       fill: none,stroke: none,font-size: 24px,color: #383a3c
    classDef container      fill: none,stroke: none
    classDef vm             fill: none,stroke: none
    classDef cni            fill: #a4d8ff,stroke: #1971c2,stroke-width: 4px,stroke-dasharray: 4 4,rx: 15,ry: 15,padding: 2150px,font-size: 32px,height: 80px,text-align:center,y: -40px
    classDef operators      fill: #b1f2bc,stroke: #2f9e44,stroke-width: 4px,stroke-dasharray: 4 4,rx: 15,ry: 15,padding: 2150px,font-size: 32px,height: 80px,text-align:center,y: -40px
    classDef services       fill: none,stroke: none,height: 10
    classDef svc            fill: #e8ecef,stroke: #5193d1,stroke-width: 2px,rx: 15,ry: 15
    classDef k8s            fill: none,stroke: none,color: #383a3c,height: 100px,y: 53
    classDef k8sicon        fill: none,stroke: none,color: #383a3c
    classDef k8slabel       fill: none,stroke: none,color: #383a3c,font-size: 24px
    classDef stack          fill: #fff,stroke: #e26061,stroke-width: 2px,color: #383a3c,rx: 15,ry: 15,height: 100px,y: 107px
    classDef stackicon      fill: none,stroke: none,color: #383a3c,height: 10px
    classDef stacklabel     fill: none,stroke: none,color: #383a3c,font-size: 24px,padding: 280px
    classDef os             fill: #ffec99,stroke: #f08c01,stroke-width: 4px,stroke-dasharray: 4 4,color: #383a3c,rx: 15,ry: 15,padding: 2150px,font-size: 32px,height: 80px,text-align:center,y: -40px
    classDef hardware       fill: #ffffff,stroke: #1e1e1e,color: #1e1e1e,stroke-width: 2px,rx: 15,ry: 15,padding: 2150px,font-size: 32px,height: 80px,text-align:center,y: -40px
```

The idea behind Genestack is simple, build an Open Infrastructure system that unites Public and Private
clouds with a platform that is simple enough for the hobbyist yet capable of exceeding the needs of the
enterprise.
