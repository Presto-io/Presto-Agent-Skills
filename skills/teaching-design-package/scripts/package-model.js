#!/usr/bin/env node
const fs = require('fs');
const crypto = require('crypto');

const inputPath = process.argv[2];
const dailyHours = Number(process.argv[3] || 8);
const calendarPath = process.argv[4];

const MODULE_REGISTRY = [
  {
    id: 'teaching-plan',
    display_name: '授课进度计划表',
    order: 1,
    work_markdown: '.teaching-design-package/work/teaching-plan.md',
    work_typst: '.teaching-design-package/work/teaching-plan.typ',
    pdf_filename: 'teaching-plan.pdf',
  },
  {
    id: 'teaching-design',
    display_name: '教学设计方案',
    order: 2,
    work_markdown: '.teaching-design-package/work/teaching-design.md',
    work_typst: '.teaching-design-package/work/teaching-design.typ',
    pdf_filename: 'teaching-design.pdf',
  },
];

const ALLOWED_FRONTMATTER = new Set([
  'course_name',
  'major_name',
  'course_attribute',
  'textbook_name',
  'class_name',
  'teachers',
  'first_teaching_day',
]);

const FORBIDDEN_FRONTMATTER = new Set([
  'daily_hours',
  'total_hours',
  'school_year',
  'semester',
  'start_date',
  'end_date',
  'date_range',
  'calendar_policy',
  'calendar_source',
  'outputs',
  'validation',
  'status',
  'manifest',
  'output_readiness',
  'final_ready',
  'pdf_ready',
  'typst_ready',
]);

function fail(code, message, extra = {}) {
  const diagnostic = { code, message, ...extra };
  console.error(`teaching-design-package.sh: ${code}: ${message}`);
  console.error(`TDPKG_DIAGNOSTIC_JSON=${JSON.stringify(diagnostic)}`);
  process.exit(1);
}

function stripQuotes(value) {
  const trimmed = String(value ?? '').trim();
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function splitFrontmatter(markdown) {
  const match = markdown.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) fail('invalid_frontmatter', 'frontmatter is required');
  return { frontmatter: match[1], body: markdown.slice(match[0].length) };
}

function parseFrontmatter(frontmatter) {
  const data = {};
  let currentListKey = '';
  for (const rawLine of frontmatter.split(/\n/)) {
    const line = rawLine.trimEnd();
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const item = line.match(/^\s*-\s*(.*)$/);
    if (item && currentListKey) {
      data[currentListKey].push(stripQuotes(item[1]));
      continue;
    }
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) fail('invalid_frontmatter', `unsupported frontmatter line: ${line}`);
    const key = match[1];
    const value = match[2];
    if (FORBIDDEN_FRONTMATTER.has(key)) {
      fail('forbidden_derived_frontmatter', `package frontmatter must not own derived field: ${key}`, { key });
    }
    if (!ALLOWED_FRONTMATTER.has(key)) {
      fail('invalid_frontmatter', `unsupported package frontmatter key: ${key}`, { key });
    }
    if (value === '') {
      data[key] = [];
      currentListKey = key;
      continue;
    }
    data[key] = stripQuotes(value);
    currentListKey = '';
  }
  for (const key of ALLOWED_FRONTMATTER) {
    if (!(key in data)) fail('invalid_frontmatter', `missing required frontmatter key: ${key}`, { key });
  }
  if (!Array.isArray(data.teachers) || !data.teachers.length) {
    fail('invalid_frontmatter', 'teachers must be a non-empty YAML list');
  }
  return data;
}

function isoDate(value, label = 'date') {
  if (!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value)) {
    fail('invalid_date', `${label} must be YYYY-MM-DD: ${value}`, { value });
  }
  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) {
    fail('invalid_date', `${label} is not a valid calendar date: ${value}`, { value });
  }
  return parsed;
}

function labelDate(date) {
  const match = date.match(/^[0-9]{4}-([0-9]{2})-([0-9]{2})$/);
  if (!match) return date;
  return `${Number(match[1])}月${Number(match[2])}日`;
}

function dateRangeLabel(start, end) {
  return `${labelDate(start)}--${labelDate(end)}`;
}

function weekdayNumber(date) {
  const value = isoDate(date).getUTCDay();
  return value === 0 ? 7 : value;
}

function weekdayName(date) {
  return ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][isoDate(date).getUTCDay()];
}

function inferTerm(scheduledStartDate) {
  const match = scheduledStartDate.match(/^([0-9]{4})-([0-9]{2})-[0-9]{2}$/);
  if (!match) fail('invalid_date', `invalid scheduled start date: ${scheduledStartDate}`, { start_date: scheduledStartDate });
  const year = Number(match[1]);
  const month = Number(match[2]);
  if (month >= 9) return { school_year: `${year}-${year + 1}学年`, semester: '第一学期' };
  return { school_year: `${year - 1}-${year}学年`, semester: '第二学期' };
}

function extractSection(markdown, heading, nextHeading) {
  const start = markdown.match(new RegExp(`^# ${heading}$`, 'm'));
  if (!start) fail('missing_section', `missing # ${heading}`, { section: heading });
  const startIndex = start.index + start[0].length;
  const rest = markdown.slice(startIndex);
  const end = nextHeading ? rest.match(new RegExp(`\\n# ${nextHeading}$`, 'm')) : null;
  return (end ? rest.slice(0, end.index) : rest).replace(/^\n+|\n+$/g, '');
}

function parsePlanRows(planText) {
  const tasks = [];
  let currentTask = null;
  let currentStage = null;
  let taskIndex = 0;
  let stageIndex = 0;
  let rowIndex = 0;
  for (const line of planText.split(/\n/)) {
    const taskMatch = line.match(/^##\s+(.+)$/);
    if (taskMatch) {
      const title = taskMatch[1].trim();
      if (!title) fail('malformed_schedule_row', 'learning task title is empty');
      taskIndex += 1;
      stageIndex = 0;
      rowIndex = 0;
      currentTask = { source: `task:${taskIndex}`, title, stages: [], rows: [], total_hours: 0 };
      tasks.push(currentTask);
      currentStage = null;
      continue;
    }
    const stageMatch = line.match(/^###\s+(.+)$/);
    if (stageMatch) {
      if (!currentTask) fail('malformed_schedule_row', `stage appears before any task: ${line}`, { line });
      const title = stageMatch[1].trim();
      if (!title) fail('malformed_schedule_row', 'learning stage title is empty');
      stageIndex += 1;
      rowIndex = 0;
      currentStage = { source: `task:${taskIndex}/stage:${stageIndex}`, title, rows: [], total_hours: 0 };
      currentTask.stages.push(currentStage);
      continue;
    }
    const content = line.trim();
    if (!content) continue;
    if (!currentTask) fail('malformed_schedule_row', `content appears before any task: ${content}`, { line: content });
    if (!currentStage) fail('malformed_schedule_row', `content appears before any stage: ${content}`, { line: content, task: currentTask.title });
    const rowMatch = content.match(/^(.+)-([0-9]+)$/);
    if (!rowMatch) fail('malformed_schedule_row', `malformed row hours, expected text-N: ${content}`, { line: content });
    const title = rowMatch[1].trim();
    const hours = Number(rowMatch[2]);
    if (!title) fail('malformed_schedule_row', `empty content before hour suffix: ${content}`, { line: content });
    if (!Number.isInteger(hours) || hours <= 0) fail('non_positive_hours', `row hours must be a positive integer: ${content}`, { line: content });
    rowIndex += 1;
    const row = {
      source: `task:${taskIndex}/stage:${stageIndex}/row:${rowIndex}`,
      title,
      hours,
      assigned_hours: hours,
      task_title: currentTask.title,
      stage_title: currentStage.title,
    };
    currentStage.rows.push(row);
    currentStage.total_hours += row.hours;
    currentTask.rows.push(row);
    currentTask.total_hours += row.hours;
  }
  if (!tasks.length) fail('missing_section', 'no schedule tasks found', { section: '授课进度计划' });
  for (const task of tasks) {
    if (!task.stages.length) fail('malformed_schedule_row', `schedule task has no stages: ${task.title}`, { task: task.title });
    if (!task.rows.length) fail('malformed_schedule_row', `schedule task has no hour rows: ${task.title}`, { task: task.title });
    for (const stage of task.stages) {
      if (!stage.rows.length) fail('malformed_schedule_row', `schedule stage has no hour rows: ${stage.title}`, { task: task.title, stage: stage.title });
    }
  }
  return tasks;
}

function loadCalendar(calendarFile) {
  let raw = '';
  try {
    raw = fs.readFileSync(calendarFile, 'utf8');
  } catch (error) {
    fail('missing_calendar_resource', `calendar resource missing: ${calendarFile}`, { calendar_path: calendarFile });
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    fail('invalid_calendar_json', `calendar is not valid JSON: ${error.message}`, { calendar_path: calendarFile });
  }
  const dates = Array.isArray(parsed) ? parsed : parsed && Array.isArray(parsed.dates) ? parsed.dates : null;
  if (!dates || !dates.length) fail('invalid_calendar_json', 'calendar must be a non-empty array of YYYY-MM-DD strings or expose dates[]', { calendar_path: calendarFile });
  const seen = new Set();
  let previous = '';
  for (const item of dates) {
    if (typeof item !== 'string' || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(item)) {
      fail('invalid_calendar_json', `calendar entry is not a YYYY-MM-DD string: ${String(item)}`, { calendar_path: calendarFile, entry: item });
    }
    isoDate(item, 'calendar entry');
    if (seen.has(item)) fail('invalid_calendar_json', `calendar contains duplicate date: ${item}`, { calendar_path: calendarFile, entry: item });
    if (previous && item <= previous) fail('invalid_calendar_json', `calendar dates must be strictly ordered: ${previous} then ${item}`, { calendar_path: calendarFile });
    seen.add(item);
    previous = item;
  }
  return {
    dates,
    sha256: crypto.createHash('sha256').update(raw).digest('hex'),
    schema: Array.isArray(parsed) ? 'array' : 'object.dates',
    path: calendarFile,
  };
}

function weekStartFor(dateText) {
  const parsed = isoDate(dateText);
  const copy = new Date(parsed.getTime());
  copy.setUTCDate(copy.getUTCDate() - (weekdayNumber(dateText) - 1));
  return copy.toISOString().slice(0, 10);
}

function daysBetween(startDate, endDate) {
  return Math.floor((isoDate(endDate).getTime() - isoDate(startDate).getTime()) / 86400000);
}

function termWeekFor(dateText, termWeekStart) {
  return Math.floor(daysBetween(termWeekStart, dateText) / 7) + 1;
}

function compactRange(values) {
  const unique = [];
  for (const value of values) {
    if (!unique.includes(value)) unique.push(value);
  }
  if (unique.length === 1) return unique[0];
  return `${unique[0]}-${unique[unique.length - 1]}`;
}

function applyRangeFromRows(target, rows) {
  const firstRow = rows[0];
  const lastRow = rows[rows.length - 1];
  const weeks = rows.flatMap((row) => row.hour_consumption.map((item) => item.term_week));
  const weekdays = rows.flatMap((row) => row.hour_consumption.map((item) => item.weekday));
  target.start_date = firstRow.start_date;
  target.end_date = lastRow.end_date;
  target.date_range = dateRangeLabel(target.start_date, target.end_date);
  target.use_time = target.date_range;
  target.term_week = compactRange(weeks);
  target.weekday = compactRange(weekdays);
}

function applyRangeFromConsumption(target) {
  const consumption = target.hour_consumption;
  const first = consumption[0];
  const last = consumption[consumption.length - 1];
  target.start_date = first.date;
  target.end_date = last.date;
  target.date_range = dateRangeLabel(target.start_date, target.end_date);
  target.use_time = target.date_range;
  target.term_week = compactRange(consumption.map((item) => item.term_week));
  target.weekday = compactRange(consumption.map((item) => item.weekday));
}

function assignSchedule(tasks, calendar, firstTeachingDay) {
  if (!Number.isInteger(dailyHours) || dailyHours <= 0) fail('non_positive_hours', `daily_hours must be a positive integer: ${dailyHours}`);
  const firstIndex = calendar.dates.indexOf(firstTeachingDay);
  if (firstIndex < 0) {
    fail('first_day_not_found', `first_teaching_day not found in calendar: ${firstTeachingDay}`, { first_teaching_day: firstTeachingDay, calendar_path: calendar.path });
  }
  const termWeekStart = weekStartFor(calendar.dates[0]);
  let currentIndex = firstIndex;
  let remainingDailyCapacity = dailyHours;
  const rowSummaries = [];

  for (const task of tasks) {
    for (const stage of task.stages) {
      for (const row of stage.rows) {
        let left = row.hours;
        row.hour_consumption = [];
        while (left > 0) {
          if (currentIndex >= calendar.dates.length) {
            fail('calendar_exhausted', 'calendar ended before all row hours were assigned', { source: row.source, title: row.title });
          }
          const currentDate = calendar.dates[currentIndex];
          const consumedHours = Math.min(left, remainingDailyCapacity);
          left -= consumedHours;
          remainingDailyCapacity -= consumedHours;
          const evidence = {
            date: currentDate,
            weekday: weekdayName(currentDate),
            weekday_number: weekdayNumber(currentDate),
            term_week: termWeekFor(currentDate, termWeekStart),
            consumed_hours: consumedHours,
            remaining_daily_capacity: remainingDailyCapacity,
            source: row.source,
          };
          row.hour_consumption.push(evidence);
          if (remainingDailyCapacity === 0) {
            currentIndex += 1;
            remainingDailyCapacity = dailyHours;
          }
        }
        applyRangeFromConsumption(row);
        row.assigned_hours = row.hours;
        row.consumption = row.hour_consumption.map((item) => ({
          date: item.date,
          weekday: item.weekday,
          hours: item.consumed_hours,
        }));
        rowSummaries.push({
          source: row.source,
          title: row.title,
          assigned_hours: row.assigned_hours,
          start_date: row.start_date,
          end_date: row.end_date,
          term_week: row.term_week,
          weekday: row.weekday,
          hour_consumption: row.hour_consumption,
        });
      }
      applyRangeFromRows(stage, stage.rows);
      stage.assigned_hours = stage.total_hours;
    }
    applyRangeFromRows(task, task.rows);
    task.assigned_hours = task.total_hours;
  }

  const allRows = tasks.flatMap((task) => task.rows);
  const course = {};
  applyRangeFromRows(course, allRows);
  const term = inferTerm(course.start_date);
  return {
    calendar: {
      path: calendar.path,
      sha256: calendar.sha256,
      schema: calendar.schema,
      policy: 'skill_local_calendar',
      teaching_dates_count: calendar.dates.length,
      first_consumable_date: calendar.dates[0],
      last_consumable_date: calendar.dates[calendar.dates.length - 1],
    },
    first_teaching_day: firstTeachingDay,
    daily_hours: dailyHours,
    daily_hours_source: 'package_default',
    total_hours: allRows.reduce((sum, row) => sum + row.assigned_hours, 0),
    term_week_start: termWeekStart,
    consumed_calendar_range: {
      start_date: course.start_date,
      end_date: course.end_date,
      use_time: course.use_time,
    },
    course: {
      start_date: course.start_date,
      end_date: course.end_date,
      date_range: course.date_range,
      use_time: course.use_time,
      term_week: course.term_week,
      weekday: course.weekday,
      school_year: term.school_year,
      semester: term.semester,
      term_label: `${term.school_year}${term.semester}`,
    },
    tasks: tasks.map((task) => ({
      source: task.source,
      title: task.title,
      assigned_hours: task.assigned_hours,
      total_hours: task.total_hours,
      start_date: task.start_date,
      end_date: task.end_date,
      date_range: task.date_range,
      term_week: task.term_week,
      weekday: task.weekday,
      stage_totals: task.stages.map((stage) => ({
        source: stage.source,
        title: stage.title,
        assigned_hours: stage.assigned_hours,
        total_hours: stage.total_hours,
        start_date: stage.start_date,
        end_date: stage.end_date,
        date_range: stage.date_range,
        term_week: stage.term_week,
        weekday: stage.weekday,
      })),
    })),
    row_consumption_summary: rowSummaries,
  };
}

function buildModuleFrontmatter(metadata, scheduling) {
  const teacherName = metadata.teacher_name;
  return {
    'teaching-plan': {
      major_name: metadata.major_name,
      course_name: metadata.course_name,
      teacher_name: teacherName,
      class_name: metadata.class_name,
      first_teaching_day: metadata.first_teaching_day,
      daily_hours: scheduling.daily_hours,
      template: 'jiaoan-jihua',
    },
    'teaching-design': {
      template: 'jiaoan-shicao',
      course_name: metadata.course_name,
      course_attribute: metadata.course_attribute,
      textbook_name: metadata.textbook_name,
      class_name: metadata.class_name,
      total_hours: scheduling.total_hours,
      teacher_name: teacherName,
      use_time: scheduling.course.use_time,
    },
  };
}

function reviewMarkers(markdown) {
  const match = markdown.match(/^## 复核标记\n([\s\S]*?)(?:\n## |\n# |$)/m);
  if (!match) return [];
  return match[1].split(/\n/).map((line) => line.trim()).filter((line) => line && line !== '无' && !line.startsWith('<!--'));
}

function parseActivityHours(designText) {
  const values = [];
  for (const match of designText.matchAll(/(?:^|\n)\s*(?:活动课时|教学活动课时|lesson_activity_hours)\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\s*(?:H|h|课时)?\s*(?=\n|$)/g)) {
    values.push(Number(match[1]));
  }
  return values;
}

const markdown = fs.readFileSync(inputPath, 'utf8');
const { frontmatter } = splitFrontmatter(markdown);
const unified = parseFrontmatter(frontmatter);
const firstTeachingDay = unified.first_teaching_day;
isoDate(firstTeachingDay, 'first_teaching_day');
const planText = extractSection(markdown, '授课进度计划', '教学设计方案');
const designText = extractSection(markdown, '教学设计方案');
if (!designText.trim()) fail('missing_module_source', '教学设计方案 section has no module body', { module: 'teaching-design' });
const tasks = parsePlanRows(planText);
const calendar = loadCalendar(calendarPath);
const scheduling = assignSchedule(tasks, calendar, firstTeachingDay);
const metadata = {
  course_name: unified.course_name,
  major_name: unified.major_name,
  course_attribute: unified.course_attribute,
  textbook_name: unified.textbook_name,
  class_name: unified.class_name,
  teachers: unified.teachers,
  teacher_name: unified.teachers.join('、'),
  first_teaching_day: firstTeachingDay,
};
const moduleFrontmatter = buildModuleFrontmatter(metadata, scheduling);
const totalHours = scheduling.total_hours;
const activityHourValues = parseActivityHours(designText);
const activityHours = activityHourValues.length ? activityHourValues.reduce((sum, value) => sum + value, 0) : null;
if (activityHours !== null && activityHours !== totalHours) {
  fail('teaching_design_hours_inconsistent', `teaching-plan total hours (${totalHours}) and teaching-design activity hours (${activityHours}) mismatch`, {
    teaching_plan_total_hours: totalHours,
    teaching_design_activity_hours: activityHours,
  });
}

const model = {
  model_version: 'phase33.module-registry-scheduling.v1',
  source_markdown: inputPath,
  metadata,
  modules: {
    registry: MODULE_REGISTRY,
    items: MODULE_REGISTRY.map((entry) => ({
      ...entry,
      frontmatter: moduleFrontmatter[entry.id],
      source_section: entry.id === 'teaching-plan' ? '# 授课进度计划' : '# 教学设计方案',
      scheduling_source: 'shared_scheduling_model',
    })),
  },
  scheduling,
  derived: {
    total_hours: totalHours,
    total_hours_label: `${totalHours}H`,
    daily_hours: scheduling.daily_hours,
    calendar_policy: scheduling.calendar.policy,
    school_year: scheduling.course.school_year,
    semester: scheduling.course.semester,
    term_label: scheduling.course.term_label,
    start_date: scheduling.course.start_date,
    end_date: scheduling.course.end_date,
    date_range: scheduling.course.date_range,
    use_time: scheduling.course.use_time,
  },
  schedule: { tasks },
  teaching_design: {
    markdown: designText,
    scheduling_source: 'shared_scheduling_model',
    analysis_blocks: (designText.match(/^## 学习任务分析$/gm) || []).length,
    activity_blocks: (designText.match(/^## 教学活动设计/gm) || []).length,
    activity_hours: {
      declared: activityHours !== null,
      values: activityHourValues,
      total_hours: activityHours,
      matches_teaching_plan: activityHours === null ? null : activityHours === totalHours,
    },
    evaluation_blocks: (designText.match(/^## 学业评价$/gm) || []).length,
  },
  resources: {
    rows: [...designText.matchAll(/^### 五、学习资源\n([\s\S]*?)(?:\n## |\n### |$)/gm)].map((match) => match[1].trim()),
  },
  review_markers: reviewMarkers(markdown),
  validation: {
    final_ready: false,
    total_hours_source: 'teaching_plan_rows',
    teaching_design_activity_hours_source: activityHours === null ? 'not_declared' : 'teaching_design_body',
    hours_cross_check: activityHours === null ? 'phase33_not_declared' : 'passed',
    calendar_policy: scheduling.calendar.policy,
    shared_scheduling_model: true,
    errors: [],
  },
  output_readiness: {
    markdown_valid: true,
    typst_ready: true,
    pdf_ready: false,
    final_ready: false,
  },
};

console.log(JSON.stringify(model, null, 2));
