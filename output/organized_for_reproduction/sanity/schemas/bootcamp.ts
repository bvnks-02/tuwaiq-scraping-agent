import {defineType, defineField} from 'sanity'
export const bootcamp = defineType({
  name: 'bootcamp',
  title: 'Bootcamp / Program (المعسكر/البرنامج)',
  type: 'document',
  // Don't conflate with page — this is the educational content type, not a page
  fields: [
    defineField({name: 'titleAr', title: 'Title (AR)', type: 'string', validation: r => r.required()}),
    defineField({name: 'slug', title: 'Slug', type: 'slug', options: {source: 'titleAr'}, validation: r => r.required()}),
    defineField({name: 'descriptionAr', title: 'Description (AR)', type: 'array', of: [{type: 'block'}], description: 'Portable Text, preserves RTL'}),
    defineField({name: 'excerpt', title: 'Excerpt', type: 'text'}),
    defineField({name: 'category', title: 'Category', type: 'reference', to: [{type: 'category'}], validation: r => r.required()}),
    defineField({name: 'scope', title: 'Scope', type: 'reference', to: [{type: 'scope'}]}),
    defineField({name: 'location', title: 'Location', type: 'reference', to: [{type: 'location'}]}),
    defineField({name: 'level', title: 'Level (كبار/ناشئين)', type: 'string', options: {list: ['كبار','ناشئين','مبتدئ','متوسط','متقدم']}}),
    defineField({name: 'language', title: 'Language', type: 'string', initialValue: 'ar'}),
    defineField({name: 'isOpen', title: 'Is Open', type: 'boolean'}),
    defineField({name: 'isPaid', title: 'Is Paid', type: 'boolean'}),
    defineField({name: 'price', title: 'Price (SAR)', type: 'number'}),
    defineField({name: 'priceWithoutVat', title: 'Price ex VAT', type: 'number'}),
    defineField({name: 'vat', title: 'VAT', type: 'number'}),
    defineField({
      name: 'dates', title: 'Dates', type: 'object', fields: [
        {name: 'start', title: 'Start', type: 'datetime'},
        {name: 'end', title: 'End', type: 'datetime'},
        {name: 'registrationEnd', title: 'Registration End', type: 'datetime'},
      ]
    }),
    defineField({name: 'media', title: 'Media', type: 'object', fields: [
      {name: 'outerImage', title: 'Outer Image URL', type: 'url'},
      {name: 'innerImage', title: 'Inner Image', type: 'url'},
      {name: 'logo', title: 'Logo', type: 'url'},
      {name: 'video', title: 'Video Embed (Vimeo iframe)', type: 'text'},
    ]}),
    defineField({name: 'learningOutcomes', title: 'Learning Outcomes (Goals)', type: 'array', of: [{type: 'object', fields: [{name: 'textAr', type: 'string', title: 'Goal (AR)'}]}]}),
    defineField({name: 'faqs', title: 'FAQs', type: 'array', of: [{type: 'object', fields: [
      {name: 'question', title: 'Question (AR)', type: 'string'},
      {name: 'answer', title: 'Answer (AR)', type: 'text'},
    ]}]}),
    defineField({name: 'features', title: 'Features', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'requirements', title: 'Requirements (AR)', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'durationText', title: 'Duration Text', type: 'string'}),
    defineField({name: 'startTimeText', title: 'Start Time Text', type: 'string'}),
    defineField({name: 'endTimeText', title: 'End Time Text', type: 'string'}),
    defineField({name: 'attendType', title: 'Attend Type', type: 'string'}),
    defineField({name: 'minimumAge', title: 'Minimum Age', type: 'number'}),
    defineField({name: 'maximumAge', title: 'Maximum Age', type: 'number'}),
    defineField({name: 'academyName', title: 'Academy Name', type: 'string'}),
    defineField({name: 'mergedPublishes', title: 'Merged Instances', type: 'array', of: [{type: 'object', fields: [
      {name: 'slug', type: 'string'}, {name: 'title', type: 'string'},
      {name: 'startDate', type: 'datetime'}, {name: 'endDate', type: 'datetime'},
      {name: 'locationName', type: 'string'},
    ]}]}),
    defineField({name: 'url', title: 'Source URL', type: 'url'}),
    defineField({name: 'sourceId', title: 'Source ID', type: 'string'}),
  ],
  preview: {select: {title: 'titleAr', subtitle: 'category.titleAr'}}
})
