---
title: "Deployment Guide"
weight: 10
type: docs
description: "Everything you need to deploy a Genestack Cloud"
simple_list: true
cascade:
  - type: docs
---

## Welcome to the Genestack Deployment Guide

Genestack is a complete operations and deployment ecosystem for Kubernetes and OpenStack. The purpose of this project is to allow hobbyists, operators, and cloud service providers the ability to build, scale, and leverage Open-Infrastructure in new and exciting ways.

Genestack’s inner workings are a blend of dark magic — crafted with Kustomize and Helm. It’s like cooking with cloud. Want to spice things up? Tweak the `kustomization.yaml` files or add those extra 'toppings' using Helm's style overrides. However, the platform is ready to go with batteries included.

![The Genestack Reference Architecture](/assets/svg/Genestack-RefArch.svg)

Genestack is making use of some homegrown solutions, community operators, and OpenStack-Helm. Everything in Genestack comes together to form cloud in a new and exciting way; all built with Open Source solutions to manage cloud infrastructure in the way you need it.

## Deployment Guide Scope

This document provides all the necessary information and instructions to deploy your own Genestack cloud.  Everything is covered, including platform prerequisites, environment bring-up, to service deployment workflows.

