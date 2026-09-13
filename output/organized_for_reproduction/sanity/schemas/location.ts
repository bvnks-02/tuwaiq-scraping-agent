import {defineType, defineField} from 'sanity'
export const location = defineType({
  name: 'location',
  title: 'Location',
  type: 'document',
  fields: [
    defineField({name: 'titleAr', title: 'Name Ar', type: 'string'}),
    defineField({name: 'slug', title: 'Slug', type: 'slug', options: {source: 'titleAr'}}),
    defineField({name: 'initiativesCount', title: 'Initiatives Count', type: 'number'}),
  ]
})
