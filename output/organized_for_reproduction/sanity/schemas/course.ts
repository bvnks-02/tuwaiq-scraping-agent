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
    defineField({name: 'duration', title: 'Duration (seconds or HH:MM:SS)', type: 'string'}),
    defineField({name: 'image', title: 'Image URL', type: 'url'}),
    defineField({name: 'video', title: 'Video', type: 'url'}),
    defineField({name: 'prerequisites', title: 'Prerequisites', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'learningOutcomes', title: 'Outcomes', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'url', title: 'Source URL', type: 'url'}),
  ]
})
