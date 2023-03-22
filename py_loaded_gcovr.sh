#!/bin/bash

GCOVR_ARGS=()
CONTEXT=3
NO_CODE=
NUM_CODE=

while [ $# -ne 0 ]; do
    case "$1" in
    --no-code)
        NO_CODE=1
        shift
        ;;
    --num-code)
        NUM_CODE="$2"
        shift 2
        ;;
    --context)
        CONTEXT="$2"
        shift 2
        ;;
    *)
        GCOVR_ARGS[${#GCOVR_ARGS}]="$1"
        shift
        ;;
    esac
done

NUM=0
TOTAL_UNCOVERD_LINES=0

gcovr "${GCOVR_ARGS[@]}" | while read Line; do
  # Get file name
  File=$(echo $Line | cut -f1 -d' ')

  # The file must exist
  [ ! -f "$File" ] && continue

  # Find start and end of actual code, not CFFI prefix and postfix
  # the cffi is add a /****(X60)/ on pre and post fix 
  Lines=$(grep -nE '/\*{60}/' "$File" | cut -f1 -d':')
  Start=$(echo $Lines | cut -f1 -d' ')
  End=$(echo $Lines | cut -f2 -d' ')

  # Get the lines
  Lines=$(echo $Line | cut -f5 -d' ' | tr ',' ' ')

  if [ ! -z $NO_CODE ]; then
    echo -n "$File: "
  fi

  # For each range
  for Range in $Lines; do
    # Begin and end of range
    A=$(echo $Range | cut -f1 -d'-' )
    B=$(echo $Range | cut -f2 -d'-' )

    # If out of actual code go to next
    [ $A -lt $Start ] && continue
    [ ! -z $B ] && { [ $B -lt $Start ] && continue; }
    [ $A -gt $End ] && continue
    [ ! -z $B ] && { [ $B -gt $End ] && continue; }

    AA=$((A - CONTEXT))
    AX=$((A - 1))
    BX=$((B + 1))
    BB=$((B + CONTEXT))

    # Print lines
    if [ -z $NO_CODE ]; then

      if [ ! -z "$NUM_CODE" ] && [ "$NUM" -ge "$NUM_CODE" ]; then
        break
      fi
      NUM=$((NUM + 1))

      if [ "$CONTEXT" -gt 0 ]; then
        if [ $A -eq $B ]; then
          echo "$File:$A:"
        else
          echo "$File:$A-$B:"
        fi

        sed -n "s/^\(.*\)$/|  \1/;${AA},${AX}p;" $File
        sed -n "s/^\(.*\)$/|> \1/;${A},${B}p;" $File
        sed -n "s/^\(.*\)$/|  \1/;${BX},${BB}p;" $File

        echo
      else
        if [ $A -eq $B ]; then
          echo -n "$File:$A:"
          sed -n "s/^\s*\(.*\)$/ \1/;${A},${B}p;" $File
        else
          echo "$File:$A-$B:"
          sed -n "s/^\(.*\)$/ \1/;${A},${B}p;" $File
        fi
      fi
    fi

    # print a single digit for a single line or a range
    if [ $A -eq $B ]; then
      TOTAL_UNCOVERD_LINES=$((TOTAL_UNCOVERD_LINES + 1))
      if [ ! -z $NO_CODE ]; then
        echo -n "$A,"
      fi
    else
      TOTAL_UNCOVERD_LINES=$((TOTAL_UNCOVERD_LINES + B - A + 1))
      if [ ! -z $NO_CODE ]; then
        echo -n "$A-$B,"
      fi
    fi
  done

  TOTAL_LINES=$((End - Start))
  echo -ne "\nTotal lines: $TOTAL_LINES"
  echo -ne "\nUncoverd lines: $TOTAL_UNCOVERD_LINES"
  echo -ne "\nPercentage: $(( 100-(TOTAL_UNCOVERD_LINES*100)/TOTAL_LINES))%"
done
