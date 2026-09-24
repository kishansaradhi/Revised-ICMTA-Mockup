/**
 * eventDataService.js
 * ─────────────────────────────────────────────────────────────────────────────
 * TEMPORARY FRONTEND DATA LAYER — localStorage prototype
 *
 * This module is the ONLY place in the application that reads or writes
 * localStorage for the Event Approval workflow.  Every other file (the Event
 * Creation Form, Admin Portal, and Events page) calls these functions.
 *
 * FUTURE BACKEND MIGRATION
 * When the MySQL/REST backend is ready, replace the implementation of each
 * function below with the matching fetch() call.  The callers do not change.
 *
 *   submitEvent(event)         → POST  /api/events
 *   getPendingEvents()         → GET   /api/admin/events?status=PENDING_APPROVAL
 *   getAllAdminEvents()         → GET   /api/admin/events
 *   getEvents()                → GET   /api/events            (APPROVED only)
 *   getEventById(id)           → GET   /api/events/:id
 *   approveEvent(id)           → POST  /api/admin/events/:id/approve
 *   rejectEvent(id)            → POST  /api/admin/events/:id/reject
 * ─────────────────────────────────────────────────────────────────────────────
 */

(function (global) {
  'use strict';

  var STORAGE_KEY = 'icmta_events_v1';

  /* ── Internal helpers ──────────────────────────────────────────────────── */

  function _load() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch (e) {
      return [];
    }
  }

  function _save(events) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
  }

  function _generateId() {
    var events = _load();
    var maxNum = 0;
    events.forEach(function (ev) {
      var match = ev.id && ev.id.match(/EVT-\d{4}-(\d+)/);
      if (match) {
        var n = parseInt(match[1], 10);
        if (n > maxNum) maxNum = n;
      }
    });
    var next = String(maxNum + 1).padStart(4, '0');
    var year = new Date().getFullYear();
    return 'EVT-' + year + '-' + next;
  }

  /* ── Public API ────────────────────────────────────────────────────────── */

  /**
   * Submit a new event for admin approval.
   * Sets status = "PENDING_APPROVAL" and assigns a unique ID.
   *
   * @param  {Object} eventData  Fields from the Event Creation Form.
   * @return {Object}            The saved event object (with id, status, submittedAt).
   */
  function submitEvent(eventData) {
    var events = _load();
    var newEvent = Object.assign({}, eventData, {
      id: _generateId(),
      status: 'PENDING_APPROVAL',
      submittedAt: new Date().toISOString()
    });
    events.push(newEvent);
    _save(events);
    return newEvent;
  }

  /**
   * Return all events with status === "PENDING_APPROVAL".
   * Admin Portal uses this to populate the approval queue.
   *
   * @return {Array}
   */
  function getPendingEvents() {
    return _load().filter(function (ev) {
      return ev.status === 'PENDING_APPROVAL';
    });
  }

  /**
   * Return ALL events regardless of status (admin view).
   *
   * @return {Array}
   */
  function getAllAdminEvents() {
    return _load();
  }

  /**
   * Return only APPROVED events.
   * Public Events page uses this — PENDING and REJECTED are never returned.
   *
   * @return {Array}
   */
  function getEvents() {
    return _load().filter(function (ev) {
      return ev.status === 'APPROVED';
    });
  }

  /**
   * Return a single event by ID (any status).
   *
   * @param  {string} id
   * @return {Object|null}
   */
  function getEventById(id) {
    return _load().find(function (ev) { return ev.id === id; }) || null;
  }

  /**
   * Approve a pending event.
   * Changes status from PENDING_APPROVAL → APPROVED.
   *
   * @param  {string} id
   * @return {boolean}  true if found and updated, false otherwise.
   */
  function approveEvent(id) {
    var events = _load();
    var found = false;
    events = events.map(function (ev) {
      if (ev.id === id) {
        found = true;
        return Object.assign({}, ev, {
          status: 'APPROVED',
          approvedAt: new Date().toISOString()
        });
      }
      return ev;
    });
    if (found) _save(events);
    return found;
  }

  /**
   * Reject a pending event.
   * Changes status from PENDING_APPROVAL → REJECTED.
   * The record is retained (not deleted) for audit history.
   *
   * @param  {string} id
   * @return {boolean}  true if found and updated, false otherwise.
   */
  function rejectEvent(id) {
    var events = _load();
    var found = false;
    events = events.map(function (ev) {
      if (ev.id === id) {
        found = true;
        return Object.assign({}, ev, {
          status: 'REJECTED',
          rejectedAt: new Date().toISOString()
        });
      }
      return ev;
    });
    if (found) _save(events);
    return found;
  }

  /* ── Export ────────────────────────────────────────────────────────────── */

  global.EventDataService = {
    submitEvent: submitEvent,
    getPendingEvents: getPendingEvents,
    getAllAdminEvents: getAllAdminEvents,
    getEvents: getEvents,
    getEventById: getEventById,
    approveEvent: approveEvent,
    rejectEvent: rejectEvent
  };

})(window);

