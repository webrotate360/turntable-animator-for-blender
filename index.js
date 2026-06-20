const fs = require('fs');
const path = require('path');
const stripComments = require('strip-comments');
const archiver = require('archiver');
const glob = require('glob');

function deleteFiles(files) {
  for (const file of files) {
    if (fs.existsSync(file)) {
      const stats = fs.statSync(file);
      if (stats.isFile()) {
        fs.unlinkSync(file);
        console.log(`File deleted: ${file}`);
      } else if (stats.isDirectory()) {
        deleteFolderRecursive(file);
        console.log(`Folder deleted: ${file}`);
      }
    } else {
      console.error(`File or folder not found: ${file}`);
    }
  }
}

function deleteFolderRecursive(folderPath) {
  if (fs.existsSync(folderPath)) {
    fs.readdirSync(folderPath).forEach((file) => {
      const curPath = path.join(folderPath, file);
      if (fs.lstatSync(curPath).isDirectory()) {
        deleteFolderRecursive(curPath);
      } else {
        fs.unlinkSync(curPath);
      }
    });
    fs.rmdirSync(folderPath);
  }
}

function createZipArchive(outputPath, files, folderName) {
  const output = fs.createWriteStream(outputPath);
  const archive = archiver('zip', { zlib: { level: 9 } });

  output.on('close', () => {
    console.log(`Zip archive created: ${outputPath}`);
	deleteFiles(files);
  });

  archive.on('error', (err) => {
    throw err;
  });

  archive.pipe(output);

  for (const file of files) {
    const stat = fs.statSync(file);
    const entryName = path.join(folderName, path.basename(file));

    if (stat.isFile()) {
      archive.file(file, { name: entryName });
    } else if (stat.isDirectory()) {
      archive.directory(file, entryName);
    }
  }

  archive.finalize();
}

function removeCommentsFromFile(file) {
  const fileContent = fs.readFileSync(file, 'utf8');
  const outputContent = stripComments(fileContent, { language: 'python' });
  fs.writeFileSync(file, outputContent, 'utf8');
}

function removeCommentsFromFolder(folderPath) {
  let editedFileCount = 0;

  const files = fs.readdirSync(folderPath);

  for (const file of files) {
    const filePath = path.join(folderPath, file);
    const fileStat = fs.statSync(filePath);

    if (fileStat.isFile() && path.extname(file) === '.py') {
      const originalContent = fs.readFileSync(filePath, 'utf8');
      removeCommentsFromFile(filePath);
      const modifiedContent = fs.readFileSync(filePath, 'utf8');

      if (originalContent !== modifiedContent) {
        editedFileCount++;
      }
    } else if (fileStat.isDirectory()) {
      editedFileCount += removeCommentsFromFolder(filePath);
    }
  }

  return editedFileCount;
}

const editedFilesCount = removeCommentsFromFolder(__dirname);
const packageName = 'webrotate-360-turntable-animator';

console.log(`Total .py edited: ${ editedFilesCount }`);

glob(__dirname + '/*.py', { nodir: true }, (err, files) => {
  if (err) {
    throw err;
  }

  createZipArchive(__dirname + '/' + packageName + '.zip', [
   __dirname + '/assets',
   __dirname + '/icons',
   ...files
  ], packageName); 
});





