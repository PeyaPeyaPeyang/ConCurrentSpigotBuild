# ConCurrentSpigotBuild

Run Spigot's BuildTools concurrently.

## Requirements
+ Python 3.7 or higher
+ RAM 256GB or higher (If you build artifacts with 8 processses
+ Ability to kill all child processes when RAM utilization exceeds 95%.

## Usage
+ Clone this repository.
+ Download the [BuildTools](https://hub.spigotmc.org/jenkins/job/BuildTools/) and locate it to project root.
+ Adjust as appropriate
  + Options for BuildTools.jar at the top of the code
  + Number of concurrent builds (adjust the value of ThreadPoolExecutor at the bottom of the code)
+ Run `python run.py`

## Disclaimer
The author assumes no responsibility if your PC hangs or breaks using this.
