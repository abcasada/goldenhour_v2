# Overview

## Introduction

This is my second attempt to build some tools to help me find ideal times for photography in various parts of the world, and explore related things.

This project also serves as a playground as I explore using AI to help write and iterate over my code.

## General concept

I enjoy photography. I wanted to investigate what locations and days of the year have longer periods of "[Golden Hour](https://en.wikipedia.org/wiki/Golden_hour_(photography))" light. Golden Hour refers to the times near sunrise and sunset when ambient lighting is softer and warmer, which can make for very pleasing sky colors, views, and photographs.

There are varying opinions on what constitutes Golden Hour. For this program, I use the same definition as the [astral](https://astral.readthedocs.io/en/latest/) library - 4 degrees below to 6 degrees above the horizon. Soon this will be more easily adjustable.

There are a few tools here, which are explained below. `GH_daterange` is more user friendly than the others and will list the Golden Hour times across a given date range.

## Future plans

Ideally I'll create a GUI that can be used to interact with these tools.

## Edge cases

### Polar day/polar night

Inside the arctic circles, there are times when the sun is near the horizon for much longer. At the poles, there are several consecutive days at the equinoxes where the sun is within the golden hour or twilight ranges all day. This program is designed to handle these cases well.

### Refraction of sunlight

When the sun is near the horizon, there is some [refraction](https://en.wikipedia.org/wiki/Atmospheric_refraction) of its light, causing the sun to become visible to a viewer on the earth at the horizon a few minutes sooner than expected (and also delaying the apparent sunset). This program does not currently account for this. Due to the variability of temperature over a very large area, it is difficult to impossible to estimate the angle of refraction of an object below 5 degrees of elevation in the sky, so it is unlikely that I will add any correction for it, except possibly above 5 degrees.

# Programs

## GH_daterange

This program was specifically designed to have a simple user interface. You simply input a start date, an end date, and a latitude, and it will display the times when golden hour begins and ends on those dates. It has a Windows executable in the latest release.

To use it, simply download the `GH_daterange` executable from the [latest release](https://github.com/abcasada/goldenhour_v2/releases/latest) folder and run it.

It uses `calculate_golden_hours` from `idealtrip.py`.

## main.py

The script `main.py` takes a list of latitudes given in DESIRED_LATITUDES (defined as a constant) and returns `data_output\GH_duration_fullyear_<timestamp>.csv`, containing the duration of "golden hour" (defined as the sun being between 4 degrees below and 6 degrees above the horizon) for every day of the year at every listed latitude. The idea is to be able to visualize what times of year have more "golden hour" light at various locations, which is ideal for photography. A quick line chart in Excel will visualize it well.

The latitudes currently listed in DESIRED_LATITUDES were from a mockup driving trip. Try replacing these with `list(range(60, 91, 5))` to get a better visualization at the latitudes where golden hour can be particularly long.

## idealtrip.py

The script `idealtrip.py` takes a list of dates and latitudes in `data_input\latitude_dates.csv` (which were presumably previously determined to be an ideal trip based on looking at results in GH_times) and returns `data_output\GH_times_<timestamp>.csv`, containing the start and end time of morning and evening golden hour for each date at the given latitude.

## tripsplit.py

WIP to take driving directions and split into days and return latitudes to use in `latitude_dates.csv`.

# Requirements

Below are the requirements for running the Python scripts natively. (The Windows executable(s) are standalone.)

## Python version

Developed on 3.13; should run on 3.6+

## Libraries

os, datetime, csv, logging, pathlib, typing, multiprocessing, psutil, astral, geopy
