#!/bin/bash

# Cadence Skills — Manual Installer
# Copies skills into ~/.claude/skills/ for direct installation without the marketplace.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SKILL=${1:-"all"}

install_decision_engine_builder() {
  echo "Installing decision-engine-builder..."
  mkdir -p "$CLAUDE_DIR/skills/decision-engine-builder"
  cp -r "$SCRIPT_DIR/decision-engine-builder/skills/decision-engine-builder/." \
        "$CLAUDE_DIR/skills/decision-engine-builder/"
  echo "  → $CLAUDE_DIR/skills/decision-engine-builder/"
}

install_advanced_skill_creator() {
  echo "Installing advanced-skill-creator..."
  mkdir -p "$CLAUDE_DIR/skills/advanced-skill-creator"
  cp -r "$SCRIPT_DIR/advanced-skill-creator/skills/advanced-skill-creator/." \
        "$CLAUDE_DIR/skills/advanced-skill-creator/"
  echo "  → $CLAUDE_DIR/skills/advanced-skill-creator/"
}

install_check_skill_security() {
  echo "Installing check-skill-security..."
  mkdir -p "$CLAUDE_DIR/skills/check-skill-security"
  cp -r "$SCRIPT_DIR/check-skill-security/skills/check-skill-security/." \
        "$CLAUDE_DIR/skills/check-skill-security/"
  echo "  → $CLAUDE_DIR/skills/check-skill-security/"
}

install_site_security_audit() {
  echo "Installing site-security-audit..."
  mkdir -p "$CLAUDE_DIR/skills/site-security-audit"
  cp -r "$SCRIPT_DIR/site-security-audit/skills/site-security-audit/." \
        "$CLAUDE_DIR/skills/site-security-audit/"
  echo "  → $CLAUDE_DIR/skills/site-security-audit/"
}

install_cc_viz() {
  echo "Installing cc-viz..."
  mkdir -p "$CLAUDE_DIR/skills/cc-viz"
  cp -r "$SCRIPT_DIR/cc-viz/skills/cc-viz/." \
        "$CLAUDE_DIR/skills/cc-viz/"
  echo "  → $CLAUDE_DIR/skills/cc-viz/"
}

echo ""
echo "Cadence Skills Installer"
echo "========================"
echo ""

case "$SKILL" in
  "decision-engine-builder") install_decision_engine_builder ;;
  "advanced-skill-creator")  install_advanced_skill_creator ;;
  "check-skill-security")    install_check_skill_security ;;
  "site-security-audit")     install_site_security_audit ;;
  "cc-viz")                  install_cc_viz ;;
  "all")
    install_decision_engine_builder
    install_advanced_skill_creator
    install_check_skill_security
    install_site_security_audit
    install_cc_viz
    ;;
  *)
    echo "Unknown skill: $SKILL"
    echo "Usage: ./install.sh [all|decision-engine-builder|advanced-skill-creator|check-skill-security|site-security-audit|cc-viz]"
    exit 1
    ;;
esac

echo ""
echo "Done. Restart Claude Code to activate."
echo ""
