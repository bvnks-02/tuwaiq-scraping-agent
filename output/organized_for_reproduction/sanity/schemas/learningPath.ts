import {defineType, defineField} from 'sanity'
export const learningPath = defineType({
  name: 'learningPath',
  title: 'Learning Path (مسار)',
  type: 'document',
  fields: [
    defineField({name: 'titleAr', title: 'Title Ar', type: 'string', validation: r => r.required()}),
    defineField({name: 'slug', title: 'Slug', type: 'slug', options: {source: 'titleAr'}}),
    defineField({name: 'descriptionAr', title: 'Description Ar', type: 'array', of: [{type: 'block'}]}),
    defineField({name: 'level', title: 'Level', type: 'string', options: {list: ['JUNIOR','MIDDLE','ADVANCED']}}),
    defineField({name: 'totalDuration', title: 'Total Duration (seconds)', type: 'number'}),
    defineField({name: 'coursesCount', title: 'Courses Count', type: 'number'}),
    defineField({name: 'learningGoals', title: 'Learning Goals', type: 'array', of: [{type: 'object', fields: [{name: 'textAr', type: 'string'}]}]}),
    defineField({name: 'courses', title: 'Courses', type: 'array', of: [{type: 'reference', to: [{type: 'course'}]}]}),
    defineField({name: 'url', title: 'Source URL', type: 'url'}),
  ]
})
