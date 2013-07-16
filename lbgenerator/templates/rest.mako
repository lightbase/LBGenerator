
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:metal="http://xml.zope.org/namespaces/metal"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>pyramid_restler Example</title>
    <style>
      table {
        border-collapse: collapse;
      }
      table, th, td {
        border: 1px solid black;
      }
      form {
        margin: 0;
        padding: 0;
      }
    </style>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js"></script>
    <script src="http://ajax.microsoft.com/ajax/jquery.templates/beta1/jquery.tmpl.min.js"></script>
  </head>

  <body>
    <h2>Bases</h2>
    <table id="things">
      <tr>
        <th>id_base</th>
        <th>nome_base</th>
        <th>xml_base</th>
        <th>GET</th>
        <th>DELETE</th>
     </tr>
      % for thing in things:
        ${self.thing(thing)}
      % endfor
    </table>

    <p>
      <a href="/api/base.json">GET collection as JSON</a>
    </p>

    <h2>Create Base</h2>

    <form id="create-member-form" method="POST" action="/api/base">
      nome_base: <input type="text" name="nome_base" /><br />
      xml_base: <input type="text" name="xml_base" /><br />
      <input type="submit" value="POST /api/base" />
    </form>

	<!--
    <h2>Edit Base</h2>

    <form id="edit-member-form" method="POST" action="#">
      <input type="text" name="id_base" /> id_base<br />
      <input type="text" name="nome_base" /> nome_base<br />
      <input type="text" name="xml_base" /> xml_base<br />
      <input type="hidden" name="$method" value="PUT" />
      <input type="submit" value="PUT /api/base/{ID}" />
    </form>

    <h2>Create Registry</h2>

    <form id="reg-member-form" method="POST" enctype="multipart/form-data" action="/api/reg/base1">
      <input type="text" name="json_reg" /> json_reg<br />
      <input type="text" name="grupos_acesso" /> grupos_acesso<br />
      <input type="submit" value="POST /api/reg/base1" />
    </form>

    <h2>Edit Registry</h2>

    <form id="reg-edit-member-form" method="POST" enctype="multipart/form-data" action="/api/reg/base1/1">
      <input type="text" name="json_reg" /> json_reg<br />
      <input type="text" name="grupos_acesso" /> grupos_acesso<br />
      <input type="hidden" name="$method" value="PUT" />
      <input type="submit" value="PUT /api/reg/base1/1"/>
    </form>

    <h2>Delete Registry</h2>

    <form id="reg-delete-member-form" method="POST" enctype="multipart/form-data" action="/api/reg/base1/1">
      <input type="hidden" name="$method" value="DELETE" />
      <input type="submit" value="DELETE /api/reg/base1/1"/>
    </form>

    <h2>Create Document</h2>

    <form id="doc-member-form" method="POST" enctype="multipart/form-data" action="/api/doc/base1">
      <input type="text" name="id_reg" /> id_reg<br />
      <input type="file" name="n1" /> blob_doc<br />
      <input type="text" name="grupos_acesso" /> grupos_acesso<br />
      <input type="submit" value="POST /api/doc/base1" />
    </form>-->

    <script id="thing-template" type="text/x-jquery-tmpl">
      ${self.thing(Thing(id_base='${id_base}', nome_base='${nome_base}', xml_base='${xml_base}'))}
    </script>

    <script>//<![CDATA[
      $(document).ready(function () {

        function onCreate (location) {
          $.ajax(location, {
            dataType: 'json',
            success: function (data) {
			  console.log(data);
              //var thing = data.results;
              var thing = data[0];
              var row = $('#thing-template').tmpl(thing).appendTo('#things');
              registerDeleteFormHandlers('#thing-' + thing.id_base);
            }
          });
        }

        function onUpdate (id, fields) {
          var tr = $('#thing-' + id);
          $.each(fields, function (i, item) {
            var name = item.name;
            if (name === 'nome_base' || name === 'xml_base') {
              tr.find('td.thing-field-' + name).html(item.value);
            }
          });
        }

        $('form#create-member-form').submit(function (e) {
          e.preventDefault();
          $.ajax(this.action, {
            type: 'POST',
            data: $(this).serialize(),
            context: this,
            success: function (data, status, xhr) {
              onCreate(xhr.getResponseHeader('Location'));
            }
          });
        });

        $('form#edit-member-form').submit(function (e) {
          e.preventDefault();
          var id = $(this).find('input[name=id_base]').first().val();
          var action = '/api/base/' + id;
          var fields = $(this).serializeArray();
          $.ajax(action, {
            type: this.method,
            data: $(this).serialize(),
            success: function (data, status, xhr) {
              if (xhr.status == 204) {
                onUpdate(id, fields);
              } else if (xhr.status == 201) {
                onCreate(xhr.getResponseHeader('Location'));
              }
            }
          });
        });

        function registerDeleteFormHandlers (selector) {
          selector = selector || 'form.delete-member-form';
          $(selector).submit(function (e) {
            e.preventDefault();
            $.ajax(this.action, {
              type: this.method,
              data: $(this).serialize(),
              context: this,
              success: function () {
                $(this).closest('tr').remove();
              }
            });
          });
        }

        registerDeleteFormHandlers();
      });
    //]]</script>
  </body>
</html>


<%def name="thing(thing)">
  <tr id="thing-${thing.id_base}">
    <td class="thing-field-id">${thing.id_base}</td>
    <td class="thing-field-nome_base">${thing.nome_base}</td>
    <td class="thing-field-xml_base">${thing.xml_base}</td>
    <td><a class="thing-get-link" href="/api/base/${thing.id_base}">GET /api/base/${thing.id_base}</a></td>
    <td>
      <form class="delete-member-form" method="POST" action="/api/base/${thing.id_base}">
        <input type="hidden" name="$method" value="DELETE" />
        <input type="submit" value="DELETE /api/base/${thing.id_base}" />
      </form>
    </td>
  </tr>
</%def>
