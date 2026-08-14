"""Shared cross-module helpers for the backend application.

Contains infrastructure reused by several feature modules: database
cursor management, security helpers, and domain utilities. Feature
modules must not be imported here to avoid circular dependencies.
"""
