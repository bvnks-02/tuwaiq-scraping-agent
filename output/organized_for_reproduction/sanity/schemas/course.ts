import {defineType, defineField} from 'sanity'
export const course = defineType({
  name: 'course',
  title: 'Course (دورة)',
  type: 'document',
  fields: [
    defineField({name: 'titleAr', title: 'Title Ar', type: 'string', validation: r => r.required()}),
    defineField({name: 'slug', title: 'Slug', type: 'slug', options: {source: 'titleAr'}}),
    defineField({name: 'descriptionAr', title: 'Description Ar', type: 'array', of: [{type: 'block'}]}),
    defineField({name: 'excerpt', title: 'Excerpt', type: 'text'}),
    defineField({name: 'level', title: 'Level', type: 'string'}),
    defineField({name: 'duration', title: 'Duration (seconds)', type: 'number'}),
    defineField({name: 'image', title: 'Image URL', type: 'url'}),
    defineField({name: 'video', title: 'Video', type: 'url'}),
    defineField({name: 'prerequisites', title: 'Prerequisites', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'objectives', title: 'Objectives (AR)', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'units', title: 'Units → Sessions', type: 'array', of: [{type: 'object', fields: [
      {name: 'title', type: 'string'}, {name: 'description', type: 'text'},
      {name: 'totalDuration', title: 'Duration (seconds)', type: 'number'}, {name: 'order', type: 'number'},
      {name: 'sessions', type: 'array', of: [{type: 'object', fields: [
        {name: 'title', type: 'string'}, {name: 'description', type: 'text'},
        {name: 'type', type: 'string'}, {name: 'duration', type: 'number'}, {name: 'order', type: 'number'},
        {name: 'quiz', type: 'object', fields: [{name: 'number_of_questions', type: 'number'}, {name: 'passing_percentage', type: 'number'}, {name: 'max_attempts', type: 'number'}]},
      ]}]},
    ]}]}),
    defineField({name: 'previewVideo', title: 'Preview Video', type: 'object', fields: [{name: 'video_source', type: 'string'}, {name: 'video_id', type: 'string'}]}),
    defineField({name: 'subscribersCount', title: 'Subscribers', type: 'number'}),
    defineField({name: 'quizzesCount', title: 'Quizzes', type: 'number'}),
    defineField({name: 'technologies', title: 'Technologies', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'programmingLanguages', title: 'Languages', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'url', title: 'Source URL', type: 'url'}),
  ]
})
