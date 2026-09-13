import {defineType, defineField} from 'sanity'
export const scope = defineType({
  name: 'scope',
  title: 'Scope / Track (المجال)',
  type: 'document',
  fields: [
    defineField({name: 'titleAr', title: 'Title Ar', type: 'string', validation: r => r.required()}),
    defineField({name: 'slug', title: 'Slug', type: 'slug', options: {source: 'titleAr'}}),
    defineField({name: 'description', title: 'Description', type: 'text'}),
    defineField({name: 'image', title: 'Scope Image', type: 'image'}),
    defineField({name: 'color', title: 'Color', type: 'string'}),
  ]
})
